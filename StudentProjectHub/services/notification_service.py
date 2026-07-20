from extensions import db
from models.notification import Notification


def notify(user_id, message, link=None):
    n = Notification(user_id=user_id, message=message, link=link)
    db.session.add(n)
    db.session.commit()
    return n


def unread_count(user_id):
    return Notification.query.filter_by(user_id=user_id, is_read=False).count()


def mark_all_read(user_id):
    Notification.query.filter_by(user_id=user_id, is_read=False).update({"is_read": True})
    db.session.commit()


def mark_one_read(notification_id, user_id):
    n = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
    if n:
        n.is_read = True
        db.session.commit()
    return n
