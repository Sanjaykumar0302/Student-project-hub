from extensions import db


class Package(db.Model):
    __tablename__ = "packages"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)          # e.g. "Basic", "Premium"
    price = db.Column(db.Integer, nullable=False)              # in INR, whole rupees
    description = db.Column(db.String(255))
    features = db.Column(db.Text)                              # newline-separated feature list
    is_active = db.Column(db.Boolean, default=True)

    projects = db.relationship("Project", backref="package", lazy=True)

    def feature_list(self):
        return [f.strip() for f in (self.features or "").split("\n") if f.strip()]

    def __repr__(self):
        return f"<Package {self.name} ₹{self.price}>"
