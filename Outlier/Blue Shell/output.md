## Agent Objective

Review the uploaded Turtle Bay Resort fieldwork photo packet and use the available universe records to reconstruct and document the March 14, 2026 landscaping makeup visit. The agent must inspect the visual evidence, OCR the handwritten field notes, identify duplicate and unrelated media, reconcile the visit details with relevant email, calendar, CRM, and messaging records, and produce consistent fieldwork documentation.

The agent should create:

1. A Markdown field report named `turtle_bay_fieldwork_report.md`.
2. A CSV photo log named `turtle_bay_photo_log.csv`.
3. An `excluded_photos` folder containing the exact duplicate and unrelated photo.

The completed documentation must distinguish historical information from observations in the uploaded packet, accurately explain the crew assignment, and avoid claiming that Lucia personally attended the visit.



## Desired Outcome

The agent must produce the following in the workspace:

1. `turtle_bay_fieldwork_report.md` containing:

* Site: Turtle Bay Resort
* Visit date: March 14, 2026
* Crew: Paloma + 2
* Lucia did not attend
* Arrival: 7:05 AM
* Departure: 2:20 PM
* Total duration: 7 hours 15 minutes
* 21 spent heliconia stems removed
* 4 plants leaning toward the path
* Path clearance increased from 22 inches to 38 inches
* Clearance improvement: 16 inches
* Leak found near valve N-3
* Irrigation test duration: 8 minutes
* Wet area: approximately 3 feet
* Recommendation: replace the clamp and retest
* Relevant CRM history clearly separated from March 14 observations
* No unsupported diagnosis of the damaged leaf

2. `turtle_bay_photo_log.csv` with exactly these columns (`filename`,`site_area`,`visible_evidence`,`field_note_match`,`assessment`,`disposition`,`rationale`)

The CSV must contain one row for every original image and use these dispositions(`IMG_6140.JPG` `retain`, `IMG_6142.JPG` `retain`, `IMG_6142_copy.JPG` `exclude_duplicate`,
IMG_6148.JPG          retain
IMG_6151.JPG          retain
IMG_6156.PNG          retain
IMG_6159.JPG          retain
IMG_5902.JPG          exclude_unrelated
field_notes_0314.jpg  retain


3. An `excluded_photos` folder containing:

```text
IMG_6142_copy.JPG
IMG_5902.JPG
```

The duplicate must be identified as an exact copy of `IMG_6142.JPG`.
`IMG_5902.JPG` must be identified as an unrelated indoor greenhouse or conservatory image.

The Markdown report and CSV must agree on all measurements, crew details, filenames, dispositions, findings, and recommendations.

The final response must confirm the two created files, the two moved images, the clamp-replacement recommendation, and that Paloma’s crew completed the visit while Lucia did not attend.



## Prompt

I need you to document the March 14, 2026 Turtle Bay Resort landscaping makeup visit using the attached fieldwork photo packet and the records available in this workspace.

Review the relevant email, calendar, CRM, and messaging records to confirm the visit schedule, crew assignment, requested work, and useful site history. Then inspect every uploaded image, including the handwritten field notes, and document the heliconia cleanup and north-lawn irrigation inspection.

Create `turtle_bay_fieldwork_report.md` with a clear account of the visit, the crew and schedule reconciliation, the measurements and findings from the field notes and photos, relevant historical context, recommended follow-up, excluded media, and any uncertainty. Keep older CRM history separate from conditions observed during this visit, and do not make a definite diagnosis from the damaged-leaf image alone.

Also create `turtle_bay_photo_log.csv` with exactly these columns:

```text
filename,site_area,visible_evidence,field_note_match,assessment,disposition,rationale
```

Include one row for every original image. Create an `excluded_photos` folder and move any exact duplicate or clearly unrelated image there instead of deleting it, explaining each decision in the photo log.

Make sure the report and CSV agree on all filenames, measurements, crew details, findings, and recommendations. In your final response, confirm the files created, identify the excluded images and why they were moved, state the main irrigation follow-up, and clarify who completed the visit.

This version keeps all important requirements while sounding a little more like a real user request.
