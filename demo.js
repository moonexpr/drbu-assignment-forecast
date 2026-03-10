function join_lines(text) {
  const lines = text.split(/\r/);
  let result = [];

	for (let i = 0; i < lines.length; i++) {
		const line = lines[i].trim().replace('\t', '');
		result.push(line);
	}

  return result.join("");
}

const sys_events = Application('System Events')
sys_events.includeStandardAdditions = true

const text = String(sys_events.theClipboard())
const clean_text = join_lines(text)
// console.log(clean_text)

const app = Application.currentApplication();
app.includeStandardAdditions = true;
app.displayDialog(clean_text);
