-- -----------------------------
-- Helper: detect substring in list item
-- -----------------------------
local function item_contains_text(item, text_match)
    for _, block in ipairs(item) do
      if block.t == "Para" or block.t == "Plain" then
        for _, inline in ipairs(block.content) do
          if inline.t == "Str" and inline.text:lower():match(text_match) then
            return true
          end
        end
      end
    end

		return false
end

-- -----------------------------
-- Helper: tests if a string starts with text
-- taken from https://gist.github.com/kgriffs/124aae3ac80eefe57199451b823c24ec
-- -----------------------------
function string:startswith(start)
    return self:sub(1, #start) == start
end

local highlight_start_sentinel = {}
local function item_apply_highlight_find_start_index(block)
	for index, item in ipairs(block.content) do
			if item.t == "RawInline" and index + 1 < #block.content then
				if item.text:startswith("\\checkbox") then
						return index + 2
				end
			end
	end

	return 1
end
--
-- -----------------------------
-- Helper: apply highlight to item, color must be either 'yellow' or 'blue'.
-- -----------------------------
local function item_apply_highlight(item, color)
		for _, block in ipairs(item) do
			if block.t == "Para" or block.t == "Plain" then
				local start = item_apply_highlight_find_start_index(block)
				table.insert(block.content, start,
					pandoc.RawInline("latex", "\\highlight" .. color .. "{"))
				table.insert(block.content,
					pandoc.RawInline("latex", "}"))
				break
			end
		end
end

-- -----------------------------
-- Highlight list items containing "John"
-- -----------------------------
function BulletList(el)
  for _, item in ipairs(el.content) do
    local contains_john = false
    if item_contains_text(item, "john") then
			item_apply_highlight(item, "Yellow")
		elseif item_contains_text(item, "reflection") then
			item_apply_highlight(item, "Blue")
		end
  end

  return el
end
