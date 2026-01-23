# Instruction: Adaptive Layout Logic

## Core Requirement
The system must prioritize keeping tailored resumes to a **single page**. 

## Implementation Logic
1.  **Initial Render**: The `src/renderer.py` first attempts to render the resume using standard margins (`0.75in` sides, `0.6in` vertical).
2.  **Detection**: After the first pass, the renderer checks the TeX log for page counts.
3.  **Dynamic Adjustment**: If the output exceeds 1 page, the renderer automatically triggers a second pass by:
    -   Reducing margins to `0.5in` sides and `0.4in` vertical.
    -   Tightening section spacing.
4.  **Preservation**: Future agents must ensure this logic remains in `Renderer.render_resume` and is not overridden by static margin hard-coding.

## User Rationale
Recruiters prefer single-page documents. If a tailored version is wordy, we adjust the layout rather than cutting content if possible.
