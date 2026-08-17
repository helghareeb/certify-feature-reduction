"""Generate cover_letter.txt from cover_letter.tex so the two cannot drift.

The journal wants a plain-text cover letter alongside the typeset one. Maintaining both by
hand is how they end up disagreeing, so the .txt is derived from the .tex and never edited.
"""
import re, datetime, textwrap, os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(HERE, "paper", "cover_letter.tex")
DST = os.path.join(HERE, "paper", "cover_letter.txt")

t = open(SRC, encoding="utf-8").read()
body = t[t.index(r"\opening{") :]
body = body[body.index("}") + 1 : body.index(r"\closing")]

# LaTeX -> plain text
body = body.replace("~", " ")
body = re.sub(r"\\textbf\{([^{}]*)\}", r"\1", body)
body = re.sub(r"\\textit\{([^{}]*)\}", r"\1", body)
body = re.sub(r"\\emph\{([^{}]*)\}", r"\1", body)
body = re.sub(r"\\href\{[^{}]*\}\{([^{}]*)\}", r"\1", body)
body = body.replace("``", '"').replace("''", '"')
body = body.replace("---", " - ").replace("--", "-")
body = body.replace(r"\$", "$")
body = re.sub(r"\$([^$]*)\$", r"\1", body)
body = body.replace("{,}", ",")
body = re.sub(r"\\[a-zA-Z]+", "", body)
body = body.replace("{", "").replace("}", "")

paras = [" ".join(p.split()) for p in body.split("\n\n") if p.strip()]

opening = re.search(r"\\opening\{([^{}]*)\}", t).group(1)
closing = re.search(r"\\closing\{([^{}]*)\}", t).group(1)

out = []
out.append("Haitham A. El-Ghareeb")
out.append("Information Systems Department")
out.append("Faculty of Computers and Information Sciences")
out.append("Mansoura University, Mansoura, Egypt")
out.append("helghareeb@mans.edu.eg")
out.append("")
out.append(datetime.date.today().strftime("%d %B %Y"))
out.append("")
out.append("The Editors")
out.append("Scientific Reports")
out.append("")
out.append(opening)
out.append("")
for p in paras:
    out.append("\n".join(textwrap.wrap(p, 92)))
    out.append("")
out.append(closing)
out.append("")
out.append("Haitham A. El-Ghareeb")

open(DST, "w", encoding="utf-8", newline="\r\n").write("\n".join(out) + "\n")
print("wrote", DST, os.path.getsize(DST), "bytes")
print()
print("\n".join(out[:22]))
