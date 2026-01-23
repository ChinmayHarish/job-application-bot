import os
import subprocess
import shutil

import re

class Renderer:
    def __init__(self, template_path="data/resume_base.tex", output_dir="output"):
        self.template_path = template_path
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def escape_latex(self, text):
        """Escapes LaTeX special characters."""
        if not text:
            return ""
        replacements = {
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '~': r'\textasciitilde{}',
            '^': r'\textasciicircum{}',
            '\\': r'\textbackslash{}',
        }
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
        return text

    def render_resume(self, tailored_latex, filename="resume.pdf", output_pdf_dir=None):
        """
        Renders a LaTeX string into a PDF.
        Supports both full LaTeX documents and partial content (for injection).
        Includes "Adaptive Layout" logic to fit content on a single page if needed.
        """
        # INJECT CONTENT OR USE FULL DOCUMENT
        if str(tailored_latex).strip().startswith(r"\documentclass"):
            final_tex = tailored_latex
        else:
            # READ TEMPLATE
            with open(self.template_path, 'r') as f:
                template = f.read()

            # Logic: Replace "Summary" section (legacy fallback)
            summary_text = ""
            if isinstance(tailored_latex, dict):
                summary_text = tailored_latex.get('summary', '')
            else:
                summary_text = str(tailored_latex)

            escaped_summary = self.escape_latex(summary_text)

            start_marker = r"\section{Summary}"
            end_marker = r"\section{Experience}"

            start_idx = template.find(start_marker)
            end_idx = template.find(end_marker)

            if start_idx != -1 and end_idx != -1:
                pre_summary = template[:start_idx + len(start_marker)]
                post_summary = template[end_idx:]
                final_tex = f"{pre_summary}\n{escaped_summary}\n{post_summary}"
            else:
                final_tex = template

        # DIRECTORIES
        # The .tex file goes to an internal archive
        tex_archive_dir = os.path.join("data", "tex_archive")
        os.makedirs(tex_archive_dir, exist_ok=True)
        
        # The .pdf goes to the requested directory (e.g., Desktop)
        pdf_dir = output_pdf_dir if output_pdf_dir else self.output_dir
        os.makedirs(pdf_dir, exist_ok=True)

        # WRITE TEMP TEX FILE in archive
        clean_filename = filename.replace(".pdf", "")
        tex_filename = f"{clean_filename}.tex"
        temp_tex_path = os.path.join(tex_archive_dir, tex_filename)
        
        with open(temp_tex_path, 'w') as f:
            f.write(final_tex)

        # FIRST PASS: COMPILE WITH TECTONIC
        pdf_path = self._compile_with_tectonic(temp_tex_path, pdf_dir, clean_filename)
        
        if not pdf_path:
            return None

        # CHECK PAGE COUNT (Adaptive Logic)
        log_path = os.path.join(pdf_dir, f"{clean_filename}.log")
        if os.path.exists(log_path):
            with open(log_path, 'r') as f:
                log_content = f.read()
                # Use regex to find "Output written on ... (X pages, ...)"
                match = re.search(r"Output written on .*? \((\d+) pages?", log_content)
                if match:
                    pages = int(match.group(1))
                    if pages > 1:
                        print(f"⚠️ PDF exceeds 1 page ({pages} pages found). Triggering Adaptive Layout (tightening margins)...")
                        # Tighten margins dynamically by replacing geography settings
                        tight_tex = final_tex.replace(
                            r"left=0.75in,right=0.75in,top=0.6in,bottom=0.6in",
                            r"left=0.5in,right=0.5in,top=0.4in,bottom=0.4in"
                        )
                        # Also tighten section spacing if possible
                        tight_tex = tight_tex.replace(
                            r"\titlespacing{\section}{0pt}{12pt}{6pt}",
                            r"\titlespacing{\section}{0pt}{8pt}{4pt}"
                        )
                        
                        # Overwrite temp tex and re-compile
                        with open(temp_tex_path, 'w') as f:
                            f.write(tight_tex)
                        
                        pdf_path = self._compile_with_tectonic(temp_tex_path, pdf_dir, clean_filename)

        return pdf_path

    def _compile_with_tectonic(self, tex_path, out_dir, clean_name):
        """Helper to run tectonic command."""
        # We use --keep-logs to ensure we can read the page count from the log
        cmd = ["tectonic", "-X", "compile", tex_path, "--outdir", out_dir, "--keep-logs"]
        try:
            print(f"Compiling {os.path.basename(tex_path)} with Tectonic...")
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            pdf_path = os.path.join(out_dir, f"{clean_name}.pdf")
            if os.path.exists(pdf_path):
                return pdf_path
        except Exception as e:
            print(f"Error compiling: {e}")
        return None
