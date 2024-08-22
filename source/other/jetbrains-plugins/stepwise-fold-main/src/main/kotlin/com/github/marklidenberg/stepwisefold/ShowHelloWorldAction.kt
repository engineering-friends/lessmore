package com.github.marklidenberg.stepwisefold

import com.intellij.notification.Notification
import com.intellij.notification.NotificationType
import com.intellij.notification.Notifications
import com.intellij.openapi.actionSystem.AnAction
import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.ui.popup.JBPopupFactory
import com.intellij.psi.PsiFile
import com.intellij.ui.GotItTooltip

const val HELLO_WORLD_NOTIFICATION_GROUP_ID = "Show Hello World triggered"

// to run this action: shift+shift -> Show Hello World
class ShowHelloWorldAction: AnAction() {
    override fun actionPerformed(e: AnActionEvent) {
        val notification = Notification(
            HELLO_WORLD_NOTIFICATION_GROUP_ID,
            MyBundle.message("Title! "),
            MyBundle.message("Text!"),
            NotificationType.INFORMATION
        )
        Notifications.Bus.notify(notification, e.project)
    }

    override fun isDumbAware() = true

}