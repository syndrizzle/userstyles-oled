import usercssMeta from "usercss-meta";
import { calcStyleDigest } from "https://github.com/openstyles/stylus/raw/8fe35a4b90d85fb911bd7aa1deab4e4733c31150/src/js/sections-util.js";

const stylesRoot = new URL("../../styles/", import.meta.url);

const settings = {
  settings: {
    updateInterval: 24,
    updateOnlyEnabled: true,
    patchCsp: true,
    "editor.linter": "",
  },
};

const data: Record<string, unknown>[] = [settings];
const styleDirs = [...Deno.readDirSync(stylesRoot)]
  .filter((entry) => entry.isDirectory)
  .sort((a, b) => a.name.localeCompare(b.name));

for (const dir of styleDirs) {
  const file = new URL(`${dir.name}/catppuccin.user.less`, stylesRoot);

  let content: string;
  try {
    content = await Deno.readTextFile(file);
  } catch (err) {
    if (err instanceof Deno.errors.NotFound) continue;
    throw err;
  }

  const { metadata } = usercssMeta.parse(content);
  const userstyle = {
    enabled: true,
    name: metadata.name,
    description: metadata.description,
    author: metadata.author,
    url: metadata.url,
    updateUrl: metadata.updateURL,
    usercssData: metadata,
    sourceCode: content,
  } as Record<string, unknown>;

  userstyle.originalDigest = await calcStyleDigest(userstyle);
  data.push(userstyle);
}

await Deno.mkdir("dist", { recursive: true });
await Deno.writeTextFile("dist/import.json", JSON.stringify(data));
