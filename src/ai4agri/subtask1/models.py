"""Lightweight segmentation models for Subtask 1 vision experiments."""

from __future__ import annotations

import torch
from torch import nn
import torch.nn.functional as F


class ConvBlock(nn.Module):
    def __init__(self, in_channels: int, out_channels: int) -> None:
        super().__init__()
        self.block = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, 3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, 3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.block(x)


class SmallUNet(nn.Module):
    def __init__(self, in_channels: int, num_classes: int = 5, base_channels: int = 32) -> None:
        super().__init__()
        c = base_channels
        self.enc1 = ConvBlock(in_channels, c)
        self.enc2 = ConvBlock(c, c * 2)
        self.enc3 = ConvBlock(c * 2, c * 4)
        self.bridge = ConvBlock(c * 4, c * 8)
        self.up3 = nn.ConvTranspose2d(c * 8, c * 4, 2, stride=2)
        self.dec3 = ConvBlock(c * 8, c * 4)
        self.up2 = nn.ConvTranspose2d(c * 4, c * 2, 2, stride=2)
        self.dec2 = ConvBlock(c * 4, c * 2)
        self.up1 = nn.ConvTranspose2d(c * 2, c, 2, stride=2)
        self.dec1 = ConvBlock(c * 2, c)
        self.head = nn.Conv2d(c, num_classes, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        e1 = self.enc1(x)
        e2 = self.enc2(F.max_pool2d(e1, 2))
        e3 = self.enc3(F.max_pool2d(e2, 2))
        bridge = self.bridge(F.max_pool2d(e3, 2))
        d3 = self.up3(bridge)
        d3 = self.dec3(torch.cat([d3, e3], dim=1))
        d2 = self.up2(d3)
        d2 = self.dec2(torch.cat([d2, e2], dim=1))
        d1 = self.up1(d2)
        d1 = self.dec1(torch.cat([d1, e1], dim=1))
        return self.head(d1)


class ResNetFPN(nn.Module):
    def __init__(self, in_channels: int, num_classes: int = 5) -> None:
        super().__init__()
        from torchvision.models import resnet18

        backbone = resnet18(weights=None)
        backbone.conv1 = nn.Conv2d(in_channels, 64, kernel_size=7, stride=2, padding=3, bias=False)
        self.stem = nn.Sequential(backbone.conv1, backbone.bn1, backbone.relu)
        self.pool = backbone.maxpool
        self.layer1 = backbone.layer1
        self.layer2 = backbone.layer2
        self.layer3 = backbone.layer3
        self.layer4 = backbone.layer4
        self.lateral4 = nn.Conv2d(512, 128, 1)
        self.lateral3 = nn.Conv2d(256, 128, 1)
        self.lateral2 = nn.Conv2d(128, 128, 1)
        self.lateral1 = nn.Conv2d(64, 128, 1)
        self.smooth = ConvBlock(128, 128)
        self.head = nn.Conv2d(128, num_classes, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        input_size = x.shape[-2:]
        c1 = self.layer1(self.pool(self.stem(x)))
        c2 = self.layer2(c1)
        c3 = self.layer3(c2)
        c4 = self.layer4(c3)
        p = self.lateral4(c4)
        p = F.interpolate(p, size=c3.shape[-2:], mode="bilinear", align_corners=False) + self.lateral3(c3)
        p = F.interpolate(p, size=c2.shape[-2:], mode="bilinear", align_corners=False) + self.lateral2(c2)
        p = F.interpolate(p, size=c1.shape[-2:], mode="bilinear", align_corners=False) + self.lateral1(c1)
        p = self.smooth(p)
        p = F.interpolate(p, size=input_size, mode="bilinear", align_corners=False)
        return self.head(p)


class TinyPatchTransformerSeg(nn.Module):
    def __init__(
        self,
        in_channels: int,
        num_classes: int = 5,
        embed_dim: int = 192,
        patch_size: int = 8,
        depth: int = 4,
        heads: int = 6,
    ) -> None:
        super().__init__()
        self.patch_size = patch_size
        self.stem = nn.Sequential(
            nn.Conv2d(in_channels, embed_dim, 3, padding=1, bias=False),
            nn.BatchNorm2d(embed_dim),
            nn.ReLU(inplace=True),
            nn.Conv2d(embed_dim, embed_dim, patch_size, stride=patch_size),
        )
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embed_dim,
            nhead=heads,
            dim_feedforward=embed_dim * 4,
            dropout=0.1,
            batch_first=True,
            activation="gelu",
            norm_first=True,
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=depth)
        self.decoder = nn.Sequential(
            nn.Conv2d(embed_dim, 128, 3, padding=1),
            nn.ReLU(inplace=True),
            nn.Upsample(scale_factor=patch_size, mode="bilinear", align_corners=False),
            ConvBlock(128, 64),
            nn.Conv2d(64, num_classes, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        patches = self.stem(x)
        height, width = patches.shape[-2:]
        tokens = patches.flatten(2).transpose(1, 2)
        encoded = self.encoder(tokens).transpose(1, 2).reshape(x.shape[0], -1, height, width)
        out = self.decoder(encoded)
        return F.interpolate(out, size=x.shape[-2:], mode="bilinear", align_corners=False)


class SamStyleOrdinalSeg(nn.Module):
    """Promptless SAM-style ViT encoder with a dense custom decoder for multispectral patches."""

    def __init__(
        self,
        in_channels: int,
        num_classes: int = 5,
        embed_dim: int = 384,
        patch_size: int = 4,
        depth: int = 8,
        heads: int = 8,
    ) -> None:
        super().__init__()
        self.patch_size = patch_size
        self.embed_dim = embed_dim
        self.low_level = nn.Sequential(
            nn.Conv2d(in_channels, 96, 3, padding=1, bias=False),
            nn.BatchNorm2d(96),
            nn.GELU(),
            nn.Conv2d(96, 96, 3, padding=1, bias=False),
            nn.BatchNorm2d(96),
            nn.GELU(),
        )
        self.patch_embed = nn.Conv2d(96, embed_dim, patch_size, stride=patch_size)
        grid = 128 // patch_size
        self.pos_embed = nn.Parameter(torch.zeros(1, grid * grid, embed_dim))
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embed_dim,
            nhead=heads,
            dim_feedforward=embed_dim * 4,
            dropout=0.1,
            batch_first=True,
            activation="gelu",
            norm_first=True,
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=depth)
        self.neck = nn.Sequential(
            nn.Conv2d(embed_dim, 256, 1, bias=False),
            nn.BatchNorm2d(256),
            nn.GELU(),
            nn.Conv2d(256, 256, 3, padding=1, bias=False),
            nn.BatchNorm2d(256),
            nn.GELU(),
        )
        self.class_queries = nn.Parameter(torch.randn(num_classes, 256) * 0.02)
        self.mask_embed = nn.Sequential(
            nn.Linear(256, 256),
            nn.GELU(),
            nn.Linear(256, 256),
        )
        self.up = nn.Sequential(
            nn.ConvTranspose2d(256, 160, 2, stride=2),
            nn.BatchNorm2d(160),
            nn.GELU(),
            nn.ConvTranspose2d(160, 96, 2, stride=2),
            nn.BatchNorm2d(96),
            nn.GELU(),
        )
        self.refine = nn.Sequential(
            nn.Conv2d(192, 128, 3, padding=1, bias=False),
            nn.BatchNorm2d(128),
            nn.GELU(),
            nn.Conv2d(128, 128, 3, padding=1, bias=False),
            nn.BatchNorm2d(128),
            nn.GELU(),
        )
        self.pixel_head = nn.Conv2d(128, 256, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        input_size = x.shape[-2:]
        low = self.low_level(x)
        patches = self.patch_embed(low)
        height, width = patches.shape[-2:]
        tokens = patches.flatten(2).transpose(1, 2)
        if tokens.shape[1] == self.pos_embed.shape[1]:
            tokens = tokens + self.pos_embed
        encoded = self.encoder(tokens).transpose(1, 2).reshape(x.shape[0], self.embed_dim, height, width)
        features = self.neck(encoded)
        up = self.up(features)
        up = F.interpolate(up, size=input_size, mode="bilinear", align_corners=False)
        refined = self.refine(torch.cat([up, low], dim=1))
        pixel_embed = self.pixel_head(refined)
        class_embed = self.mask_embed(self.class_queries)
        return torch.einsum("bchw,kc->bkhw", pixel_embed, class_embed)


def build_model(name: str, in_channels: int, num_classes: int = 5, base_channels: int = 32) -> nn.Module:
    if name == "unet":
        return SmallUNet(in_channels, num_classes=num_classes, base_channels=base_channels)
    if name == "resnet_fpn":
        return ResNetFPN(in_channels, num_classes=num_classes)
    if name in {"tiny_vit", "patch_transformer"}:
        return TinyPatchTransformerSeg(in_channels, num_classes=num_classes)
    if name in {"sam_decoder", "sam_style"}:
        embed_dim = max(256, base_channels * 6)
        heads = 8 if embed_dim % 8 == 0 else 6
        return SamStyleOrdinalSeg(in_channels, num_classes=num_classes, embed_dim=embed_dim, heads=heads)
    raise ValueError(f"unknown model: {name}")
