def register_blueprints(app):
    from routes.home import home_bp
    from routes.auth import auth_bp
    from routes.student import student_bp
    from routes.admin import admin_bp
    from routes.project import project_bp
    from routes.package import package_bp
    from routes.notification import notification_bp
    from routes.profile import profile_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp, url_prefix="/student")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(project_bp, url_prefix="/project")
    app.register_blueprint(package_bp, url_prefix="/packages")
    app.register_blueprint(notification_bp, url_prefix="/notifications")
    app.register_blueprint(profile_bp, url_prefix="/profile")
