
## Task:  Confirm any submission limits, file naming rules, and expected ZIP structure on CodaBench

Submission

The required submission is a single ZIP archive containing the segmentation results for the test subset (test.csv). Inside this archive, you must include the segmented images as PNG files. Crucially, each PNG file must be named exactly after its corresponding patch_id. The goal is to submit all 800 images; while submitting fewer is permissible, it will negatively impact your overall score, and any extraneous files beyond the expected PNGs will be ignored by the scoring system. Additionally, the predicted output must only contain integer values ranging from 0 (very low) to 4 (very high).

ALL FILES SHOULD BE ROOT OF THE ZIP (no subfolders)

Note that the true labels for the test data are hidden from participants and are retained by the organizers for evaluation.

We also strongly encourage participants to submit a PDF file explaining their method inside of the zip. In that case the name of the pdf should strictly be "report.pdf" otherwise it will be ignored. The submission of the report is optional, unless otherwise is required (see Phases and News)

Example (Pseudo code):

```python

input_loader = get_input_loader(subset="test")
model = MyModel()
for data, patch_id in input_loader:
	output = model(data)
	save_file(output, patch_id+".png")
make_zip() 
```

Evaluation

Agricultural potentials are represented by ordered classes from “very low” to “very high”. The evaluation will be conducted using the Accuracy ±1 metric, known as “Accuracy with ±1 tolerance,” which measures the proportion of predictions that are within one class of the true label. The ordinal nature of the classes allows predictions that are close to the true class to be considered partially correct. 