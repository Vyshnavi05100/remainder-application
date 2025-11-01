import time
import json
import os
from datetime import datetime
from plyer import notification

REMINDER_FILE = 'reminders.json'

# Temporary stacks for undo/redo actions
undo_stack = []
redo_stack = []

def load_reminders():
    """Load saved reminders from file."""
    if os.path.exists(REMINDER_FILE):
        with open(REMINDER_FILE, 'r') as f:
            return json.load(f)
    return []

def save_reminders(reminders):
    """Save reminders to file."""
    with open(REMINDER_FILE, 'w') as f:
        json.dump(reminders, f, indent=4)

def add_reminder():
    """Add a new reminder."""
    message = input("📝 Enter reminder message: ")
    date_str = input("📅 Enter date and time (YYYY-MM-DD HH:MM): ")

    try:
        remind_time = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
        reminders = load_reminders()
        reminders.append({
            "message": message,
            "time": remind_time.strftime("%Y-%m-%d %H:%M"),
            "notified": False
        })
        save_reminders(reminders)
        print("✅ Reminder added successfully!")
    except ValueError:
        print("❌ Invalid date/time format! Please use YYYY-MM-DD HH:MM")

def view_reminders():
    """View all reminders."""
    reminders = load_reminders()
    if not reminders:
        print("📭 No reminders found.")
        return

    print("\n🔔 Saved Reminders:")
    for i, r in enumerate(reminders, start=1):
        status = "✅ Done" if r.get("notified") else "⏳ Pending"
        print(f"{i}. {r['message']} - {r['time']} ({status})")

def delete_reminder():
    """Delete a reminder and allow undo."""
    global undo_stack, redo_stack
    reminders = load_reminders()
    if not reminders:
        print("📭 No reminders to delete.")
        return

    view_reminders()
    try:
        choice = int(input("\n❓ Enter the number of the reminder to delete: "))
        if 1 <= choice <= len(reminders):
            removed = reminders.pop(choice - 1)
            undo_stack.append(removed)
            redo_stack.clear()  # clear redo history after new delete
            save_reminders(reminders)
            print(f"🗑️ Deleted reminder: '{removed['message']}'")
        else:
            print("❌ Invalid choice number.")
    except ValueError:
        print("❌ Please enter a valid number.")

def undo_delete():
    """Undo the last deleted reminder."""
    global undo_stack, redo_stack
    if not undo_stack:
        print("⚠️ Nothing to undo.")
        return

    last_deleted = undo_stack.pop()
    reminders = load_reminders()
    reminders.append(last_deleted)
    redo_stack.append(last_deleted)
    save_reminders(reminders)
    print(f"↩️ Restored reminder: '{last_deleted['message']}'")

def redo_delete():
    """Redo the last undone delete."""
    global undo_stack, redo_stack
    if not redo_stack:
        print("⚠️ Nothing to redo.")
        return

    to_redo = redo_stack.pop()
    reminders = load_reminders()
    # Remove the matching reminder again
    reminders = [r for r in reminders if r != to_redo]
    undo_stack.append(to_redo)
    save_reminders(reminders)
    print(f"↪️ Re-deleted reminder: '{to_redo['message']}'")

def check_reminders():
    """Check and send notifications for due reminders."""
    reminders = load_reminders()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    for reminder in reminders:
        if reminder["time"] <= now and not reminder.get("notified", False):
            notification.notify(
                title="⏰ Reminder Alert!",
                message=reminder["message"],
                timeout=10
            )
            print(f"🔔 Reminder: {reminder['message']}")
            reminder["notified"] = True

    save_reminders(reminders)

def main():
    print("=== 🗓️ Python Reminder Application ===")
    while True:
        print("\n1️⃣ Add Reminder")
        print("2️⃣ View Reminders")
        print("3️⃣ Check Reminders")
        print("4️⃣ Delete Reminder")
        print("5️⃣ Undo Delete")
        print("6️⃣ Redo Delete")
        print("7️⃣ Exit")
        choice = input("👉 Enter your choice: ")

        if choice == '1':
            add_reminder()
        elif choice == '2':
            view_reminders()
        elif choice == '3':
            check_reminders()
        elif choice == '4':
            delete_reminder()
        elif choice == '5':
            undo_delete()
        elif choice == '6':
            redo_delete()
        elif choice == '7':
            print("👋 Exiting Reminder App.")
            break
        else:
            print("❌ Invalid choice, please try again.")

        time.sleep(1)

if __name__ == "__main__":
    main()
