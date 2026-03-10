-- =============================
-- checkboxes.lua
-- =============================

-- Counter for unique checkbox field names
local counter = 0

-- Wrap entire document in a checklist environment
-- function Pandoc(doc)
--   local blocks = {pandoc.RawBlock("latex", "\\begin{checklist}")}
--   for _, blk in ipairs(doc.blocks) do
--     table.insert(blocks, blk)
--   end
--   table.insert(blocks, pandoc.RawBlock("latex", "\\end{checklist}"))
--   doc.blocks = blocks
--   return doc
-- end

-- Detect substring
local function contains_john(inlines)
  for _, inline in ipairs(inlines) do
    if inline.t == "Str" and string.find(string.lower(inline.text), "John") then
      return true
    end
  end
  return false
end


-- Convert Markdown glyphs to PDF checkboxes
function Str(el)
  if el.text == "☐" then
    counter = counter + 1
    return pandoc.RawInline("latex", string.format("\\checkbox{%d}", counter))
  elseif el.text == "☒" or el.text == "☑" then
    counter = counter + 1
    return pandoc.RawInline("latex", string.format("\\checkboxlocked{%d}", counter))
  end
end

