package com.github.marklidenberg.stepwisefold

import com.intellij.notification.Notification
import com.intellij.notification.NotificationType
import com.intellij.notification.Notifications
import com.intellij.openapi.actionSystem.AnAction
import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.actionSystem.CommonDataKeys
import com.intellij.openapi.ui.popup.JBPopupFactory
import com.intellij.psi.PsiDocumentManager
import com.intellij.psi.PsiFile
import com.intellij.ui.GotItTooltip

class FoldCustomRegionsAction : AnAction("Fold Wise") {
    override fun actionPerformed(e: AnActionEvent) {
        val editor = e.getData(CommonDataKeys.EDITOR) ?: return
        val project = e.getData(CommonDataKeys.PROJECT) ?: return
        val psiFile = PsiDocumentManager.getInstance(project).getPsiFile(editor.document) ?: return
        val foldingModel = editor.foldingModel

        foldingModel.runBatchFoldingOperation {
            for (foldRegion in foldingModel.allFoldRegions) {
                if (foldRegion.placeholderText == "...←") {
                    foldRegion.isExpanded = false
                }
            }
        }
    }
}