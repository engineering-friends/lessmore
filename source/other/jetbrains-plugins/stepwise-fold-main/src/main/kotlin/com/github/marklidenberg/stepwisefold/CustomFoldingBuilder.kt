package com.github.marklidenberg.stepwisefold

import com.intellij.lang.ASTNode
import com.intellij.lang.folding.FoldingBuilderEx
import com.intellij.lang.folding.FoldingDescriptor
import com.intellij.openapi.editor.Document
import com.intellij.openapi.util.TextRange
import com.intellij.psi.PsiElement
fun parseIndentBlocks(code: String): List<Pair<Int, Int>> {
    // Return if text is empty
    if (code.trim().isEmpty()) {
        return emptyList()
    }

    // Split text into lines
    val lines = listOf("SOF") + code.split("\n").map { "    $it" } + "EOF"

    // Initialize stacks and result list
    val indentsStack = mutableListOf(-1) // stub value
    val startLineNumberStack = mutableListOf(-1) // stub value
    val result = mutableListOf<Pair<Int, Int>>()

    // Iterate over lines
    for ((i, line) in lines.withIndex()) {
        val indent = if (line.trim().isEmpty()) {
            indentsStack.last()
        } else {
            line.length - line.trim().length
        }

        // Close or open the group
        while (indent < indentsStack.last()) {
            val startLine = startLineNumberStack.removeAt(startLineNumberStack.size - 1)
            result.add(Pair(startLine - 1, i - 1)) // -1 because of the SOF line
            indentsStack.removeAt(indentsStack.size - 1)
        }

        if (indent > indentsStack.last()) {
            indentsStack.add(indent)
            startLineNumberStack.add(i)
        }

        require(indent == indentsStack.last()) { "Indent mismatch" }
    }

    // Return the result: symbol ranges
    val indentBlocks = mutableListOf<Pair<Int, Int>>()

    // Calculate symbol positions for lines
    val lineEndings = mutableListOf(code.lines().first().length)
    for (line in code.lines().drop(1)) {
        lineEndings.add(lineEndings.last() + line.length + 1)
    }

    // Calculate symbol ranges
    for ((startLine, endLine) in result) {
        val start = if (startLine != 0) lineEndings[startLine - 1] + 1 else 0
        val end = lineEndings[endLine - 1]
        indentBlocks.add(Pair(start, end))
    }

    // Remove blocks with 0 length
    return indentBlocks.filter { it.first != it.second }
}

fun parseRanges(code: String): List<Pair<Int, Int>> {
    // Return if empty code
    if (code.trim().isEmpty()) {
        return emptyList()
    }

    // Parse indent blocks first
    val indentBlocks = parseIndentBlocks(code)

    // Iterate over indent blocks, find necessary ranges
    val ranges = mutableListOf<Pair<Int, Int>>()

    for ((blockStart, blockEnd) in indentBlocks.asReversed()) {
        // Init block ranges
        val lineRanges = mutableListOf<Pair<Int, Int>>()

        // Crop code
        val blockCode = code.substring(blockStart, blockEnd)

        // Split the lines
        val lines = blockCode.split("\n")

        // Calc indent
        val indent = lines.first().length - lines.first().trimStart().length

        // Iterate over lines, add ranges to the result
        var currentStart: Int? = lines.indexOfFirst { it.trim().isNotEmpty() }
        var prevStepI: Int? = null

        for ((i, line) in lines.withIndex()) {
            if (line.trim().isEmpty()) continue

            if (line.substring(indent).startsWith("# -")) {
                if (currentStart != null) {
                    lineRanges.add(Pair(currentStart, i))
                }
                currentStart = null
                prevStepI = i
            }

            if (!line.substring(indent).startsWith("# -") && currentStart == null) {
                currentStart = prevStepI
            }
        }

        // Add the last one
        if (currentStart != null) {
            lineRanges.add(Pair(currentStart, lines.indexOfLast { it.trim().isNotEmpty() } + 1))
        }

        // Remove the first one if it's all empty lines
        if (lines.subList(lineRanges.first().first, lineRanges.first().second).joinToString("\n").trim().isEmpty()) {
            lineRanges.removeAt(0)
        }

        // Remove if there is only one block (meaning no step found)
        if (lineRanges.size == 1) continue

        // Get symbol ranges and append to the result
        val _ranges = mutableListOf<Pair<Int, Int>>()

        // Calculate symbol positions for lines
        val lineEndings = mutableListOf(lines.first().length)
        for (line in lines.drop(1)) {
            lineEndings.add(lineEndings.last() + line.length + 1)
        }

        // Iterate over line blocks and calculate the start and end positions
        for ((i, j) in lineRanges) {
            var start = if (lines[i].substring(indent).startsWith("# -")) lineEndings[i] else 0
            var end = lineEndings[j - 1]

            // try to reduce the end
            while (blockCode[end - 1].isWhitespace()) {
                end -= 1
            }

            _ranges.add(Pair(start + blockStart, end + blockStart))
        }

        ranges.addAll(_ranges)
    }

    // Return the result
    return ranges.filter { it.first != it.second }
}



class CustomFoldingBuilder : FoldingBuilderEx() {
    override fun buildFoldRegions(root: PsiElement, document: Document, quick: Boolean): Array<FoldingDescriptor> {
        val descriptors: MutableList<FoldingDescriptor> = ArrayList()

        // - Collect indent blocks
        val ranges = parseRanges(document.text)

        // iterate over blocks
        for (range in ranges) {
            descriptors.add(FoldingDescriptor(root.node, TextRange(range.first, range.second)))
//            println(range)
        }
        return descriptors.toTypedArray()
    }

    override fun getPlaceholderText(node: ASTNode): String = "...←"

    override fun isCollapsedByDefault(node: ASTNode): Boolean = false
}
