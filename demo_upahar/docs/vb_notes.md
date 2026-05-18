# VB Notes

## Key Unique Asks

Yes, you can build a system that provides this remote-sensing intelligence. But the unique ask is not “build an ML
  model.” It is to build an operational agriculture intelligence platform that turns imagery into decisions: crop maps,
  health alerts, acreage, yield, procurement planning, advisories, disaster response, and auditable reports.

  Key Unique Asks

  1. Compliant multi-date imagery intelligence
     The RFP wants <=3 m optical imagery, 5-7 day temporal cadence, at least four crop-stage dates per season, Kharif
     and Rabi coverage, preprocessing, mosaicking, cloud masking, and SAR fallback during cloud/monsoon periods.
  2. Parcel-level crop intelligence
     Not just district heatmaps. The system must classify crops at parcel/village/block/district levels, attach
     confidence scores, detect multi-cropping/intercropping, and work even when cadastral data is incomplete.
  3. Ground-truth driven model improvement
     GT surveys must cover 1-2% of sown area, use stratified sampling, collect geo-tagged/photos/attributes, reserve 30%
     for independent validation, and feed model improvement every season.
  4. Crop identification with defensible accuracy
     The key intelligence ask is crop classification using multi-temporal phenology, NDVI/EVI/SAVI/NDWI/red-edge
     features, ML/rule-based refinement, confusion matrices, class-wise accuracy, and confidence per parcel.
  5. Crop health and stress monitoring
     Detect moisture stress, nutrient issues, pest/disease signals, flood/waterlogging, drought, severity categories,
     and alerts for field inspection.
  6. Acreage, change, and production intelligence
     Detect crop extent, fallow-to-crop transitions, failed crops, re-sown patches, harvested vs sown area, and village/
     block/district acreage summaries.
  7. Yield and procurement planning
     Convert crop acreage + vegetation trends + weather/soil/CCE data into production estimates, then support MSP
     procurement planning, token capacity, PACS load, and paddy supply forecasting.
  8. Action layer: advisories
     Intelligence must produce action: department advisories, extension advisories, farmer advisories, and field
     verification workflows.
  9. Disaster monitoring
     Flood mapping, waterlogging, crop-loss assessment, drone-satellite hybrid workflows, and event-based reporting.
  10. DAC/WebGIS/platform operations
     The tender asks for a Data Analytics Centre, WebGIS, mobile app, OGC/API services, integrations, reports, testing,
     training, O&M, and helpdesk. That is what makes it a platform, not a model.

  Can You Build It?
  Yes, in staged form.

  For the demo/proposal, you can build a credible version now:

  - same-area imagery;
  - aligned parcel overlays;
  - temporal crop states;
  - ML capability panel;
  - GeoJSON/backend APIs;
  - SAR/NISAR fallback positioning;
  - Section 12 traceability;
  - demo storyline and budget.

  For a real pilot, you need:

  - licensed or approved imagery;
  - real AOI boundaries;
  - GT sample plan;
  - model artifact from actual data;
  - validation metrics;
  - one district/block scope.

  For production, you need:

  - imagery procurement pipeline;
  - PostGIS/COG/map services;
  - field mobile workflow;
  - ML operations;
  - integrations with AgriStack, land records, Food Dept/MARKFED/PACS/weather;
  - O&M and security.

  The defensible pitch is: we can build the remote-sensing intelligence platform, but production accuracy and compliance
  depend on imagery access, GT data, and integration permissions.

  ## Competitors

  Companies Publicly Doing Parts Of This
  | Company | What they publicly show | Relevance |
  |---|---|---|
  | Cropin | AI agri-food platform, remote monitoring, crop detection, yield estimation, stress detection, plot scoring
  | Very close to your broad product thesis |
  | SatSure | EO decision intelligence for agriculture, crop monitoring, harvest progression, insurance/BFSI use cases |
  Strong India-relevant competitor |
  | MapMyCrop | Satellite AI crop monitoring, farm boundaries, enterprise ag intelligence | Direct crop-monitoring
  competitor |
  | EOS Data Analytics | EOSDA Crop Monitoring, satellite analytics, crop health, API access | Direct SaaS/API
  competitor |
  | EarthDaily Agro / Geosys | Field-level crop intelligence, change detection, yield forecasting, EO analytics | Strong
  enterprise-grade competitor |
  | Syngenta Cropwise | Satellite imagery, NDVI, crop health, scouting, Planet imagery integration | Strong distribution
  via agronomy network |
  | BASF xarvio | Satellite biomass maps, disease/risk models, field-zone recommendations | Strong agronomic decision
  layer |
  | Trimble Agriculture | Calibrated crop health imagery, scouting, farm management tooling | Strong precision-ag
  workflow competitor |
  | Taranis | AI crop intelligence with high-resolution aerial/drone/leaf-level imagery plus satellite inputs | Strong
  “actionable agronomy” competitor |
  | RMSI Cropalytics | Remote sensing, GIS, crop/weather modeling for governments, insurance, commodities | Very
  relevant India/government competitor |
  | Pixxel | Hyperspectral imagery for crop classification and crop health | More data/product infrastructure than
  workflow platform, but strategically important |

  Companies That Could Be Doing This Privately
  This is inference, not verified public product evidence.

  | Category | Likely players | Why they may have hidden/private capability |
  |---|---|---|
  | Commodity traders | Cargill, ADM, Bunge, Olam, COFCO | They care about acreage, yield, supply risk, harvest timing,
  and commodity forecasts. They may use internal EO models without selling them. |
  | Insurers/reinsurers | Swiss Re, Munich Re, AXA Climate, agricultural insurers | They use remote sensing for crop
  insurance, drought, flood, parametric products, and claims. Much of this is internal or partner-delivered. |
  | Imagery providers | Planet, Maxar, Airbus, Pixxel, Satellogic | They have data access and analytics teams. They
  often sell imagery or partner with vertical platforms rather than expose full ag products. |
  | GIS/platform vendors | Esri, MapmyIndia, UP42, Google Earth Engine ecosystem, Microsoft Planetary Computer ecosystem
  | They provide infrastructure that customers build intelligence products on top of. |
  | Large SIs / government vendors | TCS, Infosys, Wipro, LTI, Tech Mahindra, NIIT GIS/Esri India, RMSI | They can
  assemble RFP-specific systems, often not marketed as standalone products. |
  | Ag input / seed / crop protection majors | Bayer, Syngenta, BASF, Corteva | They already have digital ag platforms
  and proprietary agronomy data. Some intelligence may be embedded in advisory products rather than sold as EO APIs. |

Companies That Span Domains
  | Company | Spans Domains? | Notes |
  |---|---|---|
  | Planet | Yes | Agriculture, forestry, infrastructure, civil government, defense, energy monitoring. |
  | Maxar | Yes | High-resolution imagery and intelligence for defense, mapping, telecom, energy, disaster, government.
  |
  | Airbus / UP42 | Yes | EO marketplace/workflow platform across mining, utilities, engineering, infrastructure, and
  analytics. |
  | ICEYE | Yes | SAR-based flood, insurance, government disaster response, utilities, energy, maritime/security. |
  | BlackSky | Yes | Real-time geospatial intelligence for defense, national security, economic and infrastructure
  monitoring. |
  | Descartes Labs / EarthDaily | Yes | Geospatial analytics across agriculture, sustainability, mining, insurance,
  energy, shipping, finance. |
  | Orbital Insight | Yes | Supply chain, retail, energy, finance, national security, economic indicators. |
  | Kayrros | Yes | Energy, methane, climate, carbon, asset monitoring, environmental intelligence. |
  | SatSure | Yes | Agriculture, BFSI, infrastructure, decision intelligence, India-relevant. |
  | RMSI / Cropalytics | Yes | Government, insurance, agriculture, commodities, GIS/remote sensing services. |
  | Pixxel | Potentially yes | Hyperspectral data for agriculture, environment, mining, energy, disaster response. |
  | Esri / Google Earth Engine / Microsoft Planetary Computer / Sentinel Hub | Yes | More platform/infrastructure than
  vertical intelligence product. |

  Companies Likely Doing This Privately
  This is inference, not public confirmation:

  - commodity traders: Cargill, ADM, Bunge, Olam, COFCO;
  - reinsurers/insurers: Swiss Re, Munich Re, AXA Climate;
  - energy majors: Shell, BP, Exxon, TotalEnergies, Aramco;
  - hedge funds / quant funds;
  - logistics and shipping firms;
  - national governments and defense agencies;
  - large engineering/infrastructure companies.

  They may not expose it publicly because the value is proprietary intelligence.


## Other Applications

Other High-Value Applications
  | Domain | Intelligence Product | Buyer |
  |---|---|---|
  | Insurance / disaster | Flood extent, flood depth, storm damage, wildfire scar, crop/property loss, claims triage |
  Insurers, reinsurers, governments |
  | Infrastructure / utilities | Vegetation encroachment, asset damage, construction progress, right-of-way monitoring |
  Power utilities, rail, roads, telecom |
  | Mining | Stockpile estimation, pit expansion, tailings risk, illegal mining, compliance monitoring | Mining firms,
  regulators, insurers |
  | Energy | Oil tank levels, solar/wind asset monitoring, pipeline corridor risk, flaring, methane detection | Energy
  companies, traders, regulators |
  | Forestry / carbon | Deforestation, degradation, biomass/carbon MRV, fire risk, illegal logging | Carbon projects,
  governments, NGOs |
  | Water / climate | Reservoir levels, drought, irrigation extent, waterlogging, water quality proxies | Utilities,
  climate funds, agriculture agencies |
  | Urban / real estate | Construction progress, land-use change, encroachment, roof/solar potential, informal
  settlement growth | Cities, developers, lenders |
  | Supply chain / commodities | Port activity, facility activity, storage levels, harvest/production signals | Traders,
  hedge funds, manufacturers |
  | Security / maritime | Vessel detection, port monitoring, border activity, critical infrastructure change |
  Governments, defense, maritime security |


