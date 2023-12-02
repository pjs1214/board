from django.db import models

# Create your models here.
class Post(models.Model):
    author = models.CharField(max_length=10, null=False)
    postname = models.CharField(max_length=50, null=False)
    contents = models.TextField()
    c_date = models.DateTimeField(auto_now_add=True)
    m_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.postname

"""class Reply(models.Model):
    reply_id = models.BigAutoField(primary_key=True)
    post = models.ForeignKey()
    author = models.CharField(max_length=10, null=False)
    contents = models.TextField()
    c_date = models.DateTimeField(auto_now_add=True)
    m_date = models.DateTimeField(auto_now=True)"""