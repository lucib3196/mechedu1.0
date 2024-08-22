from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class EduModule(db.Model):
    __tablename__ = "edu_module"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    folders = db.relationship("Folder", backref="edu_module", lazy=True)

    def __repr__(self):
        return f"<EduModule {self.name}>"

class Folder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    files = db.relationship('File', backref='folder', lazy=True)
    module_id = db.Column(db.Integer, db.ForeignKey('edu_module.id'), nullable=False)

    def __repr__(self):
        return f"<Folder {self.name}>"


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(256), nullable=False)
    content = db.Column(db.String, nullable=False)
    folder_id = db.Column(db.Integer, db.ForeignKey('folder.id'), nullable=False)

    def __repr__(self):
        return f"<File {self.filename} in folder {self.folder_id}>"
