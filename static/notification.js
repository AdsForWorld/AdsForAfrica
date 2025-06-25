// notifications.js

class NotificationSystem {
    constructor() {
        // Create container for notifications
        this.container = document.createElement('div');
        this.container.style.cssText = `
            position: fixed;
            top: 0;
            right: 0;
            max-width: 400px;
            margin: 10px;
            z-index: 9999;
        `;
        document.body.appendChild(this.container);
        
        // Store active notifications
        this.activeNotifications = [];
        
        // Load notifications on startup
        this.loadNotificationsFromFile();
    }

    async loadNotificationsFromFile() {
        try {
            const response = await fetch('warnings.txt');
            const text = await response.text();
            
            if (text.trim()) {
                const notifications = text.split('\n').filter(line => line.trim());
                notifications.forEach(notif => {
                    const [title, content, type] = notif.split(':');
                    this.addNotification(title, content, parseInt(type));
                });
            }
        } catch (error) {
            console.error('Error loading notifications:', error);
        }
    }

    addNotification(title, content, type = 0) {
        const notificationId = Date.now() + Math.random();
        
        // Create notification element
        const notification = document.createElement('div');
        notification.id = `notification-${notificationId}`;
        
        // Set notification style based on type
        const typeStyles = {
            0: { bg: '#e3f2fd', border: '#2196f3', text: '#0d47a1' }, // Blue - notification
            1: { bg: '#fff3e0', border: '#ff9800', text: '#e65100' }, // Orange - status
            2: { bg: '#fff8e1', border: '#ffc107', text: '#ff6f00' }, // Yellow - warning
            3: { bg: '#ffebee', border: '#f44336', text: '#b71c1c' }  // Red - error
        };
        
        const style = typeStyles[type] || typeStyles[0];
        
        notification.style.cssText = `
            background-color: ${style.bg};
            border-left: 4px solid ${style.border};
            color: ${style.text};
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 4px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            animation: slideIn 0.3s ease-out;
            position: relative;
        `;

        // Add animation keyframes
        if (!document.querySelector('#notification-animations')) {
            const style = document.createElement('style');
            style.id = 'notification-animations';
            style.textContent = `
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
                @keyframes slideOut {
                    from { transform: translateX(0); opacity: 1; }
                    to { transform: translateX(100%); opacity: 0; }
                }
            `;
            document.head.appendChild(style);
        }

        // Create content
        notification.innerHTML = `
            <div style="margin-right: 20px;">
                <strong style="display: block; margin-bottom: 5px;">${title}</strong>
                <div>${content}</div>
            </div>
            <button style="
                position: absolute;
                top: 10px;
                right: 10px;
                background: none;
                border: none;
                color: ${style.text};
                cursor: pointer;
                font-size: 20px;
                padding: 0;
                line-height: 1;
            ">×</button>
        `;

        // Add close button functionality
        const closeButton = notification.querySelector('button');
        closeButton.onclick = () => this.removeNotification(notificationId);

        // Add to container and active notifications
        this.container.appendChild(notification);
        this.activeNotifications.push(notificationId);

        return notificationId;
    }

    removeNotification(id) {
        const notification = document.getElementById(`notification-${id}`);
        if (notification) {
            notification.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => {
                notification.remove();
                this.activeNotifications = this.activeNotifications.filter(n => n !== id);
            }, 300);
        }
    }

    removeAll() {
        [...this.activeNotifications].forEach(id => this.removeNotification(id));
    }
}

// Create and export singleton instance
const notificationSystem = new NotificationSystem();
export default notificationSystem;