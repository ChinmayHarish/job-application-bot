import os
import subprocess

class Renderer:
    def __init__(self):
        # We assume tectonic is in PATH. If not, it will fail gracefully.
        pass

    def render_resume(self, content, filename="output/resume_tailored.pdf"):
        """
        Takes the tailored resume dict/content and compiles the LaTeX.
        For now, content is just the string to write to .tex
        """
        base_name = filename.replace(".pdf", "")
        tex_path = base_name + ".tex"
        
        # Write tailored content to .tex
        with open(tex_path, 'w') as f:
            f.write(content)
            
        print(f"Compiling {tex_path} with Tectonic...")
        try:
            # Run Tectonic to generate PDF
            # -X compile is the modern command pattern
            # --outdir allows us to specify where the PDF goes
            out_dir = os.path.dirname(filename)
            subprocess.run(["tectonic", tex_path, "--outdir", out_dir], check=True)
            return filename
        except Exception as e:
            print(f"PDF Rendering failed: {e}")
            return None
