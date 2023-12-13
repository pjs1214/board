from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import authenticate, login
from .forms import UserForm
from .models import Post, Reply, Img, File
import os
from django.conf import settings
from django.http import FileResponse
from django.core.files.storage import FileSystemStorage
import urllib
from django.core.paginator import Paginator


def getReply(post_id):
    l = []
    r = Reply.objects.filter(post_id=post_id)
    for i in r:
        if not i.re_id:
            l.append(i)
        else:
            b = False
            for ii in l[l.index(i.re_id)+1:]:
                if ii.depth <= i.re_id.depth:
                    l.insert(l.index(ii), i)
                    b = True
                    break
            if not b:
                l.append(i)
    return l


def chkEmpty(contents):
    if contents == "":
        return True
    else:
        for i in contents:
            if i != " ":
                return False
        return True

# Create your views here.


def home(request):
    page = request.GET.get('page', '1')
    postlist = Post.objects.order_by('-c_date')
    paginator = Paginator(postlist, 3)
    page_obj = paginator.get_page(page)
    context = {'postlist': page_obj}

    return render(request, "home.html", context)


def signup(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/')
    else:
        form = UserForm()
    return render(request, 'signup.html', {'form': form})


def write(request):
    if not request.user.is_authenticated:
        return redirect("/login/")
    else:
        if request.method == "POST":
            postname = request.POST['postname']
            contents = request.POST['contents']
            if chkEmpty(postname) or chkEmpty(contents):
                return render(request, "write.html", {'error': "빈 값이 있습니다."})
            b = Post(author=request.user.get_username(), postname=request.POST['postname'],
                     contents=request.POST['contents'])
            b.save()
            for img in request.FILES.getlist('imgs'):
                image = Img(post_id=b, img=img)
                image.save()
            for file in request.FILES.getlist('files'):
                f = File(post_id=b, file=file, content_type=file.content_type, name=os.path.basename(file.name))
                f.save()
            return redirect("/")
        else:
            return render(request, "write.html")


def modify(request, post_id):
    post = Post.objects.get(id=post_id)
    if not request.user.is_authenticated:
        return redirect("/login/")
    else:
        if post.author != request.user.get_username():
            return redirect("/post/" + str(post_id))
        else:
            if request.method == "POST":
                postname = request.POST['postname']
                contents = request.POST['contents']
                if chkEmpty(postname) or chkEmpty(contents):
                    return render(request, "modify.html", {'post': post, 'post_id': post_id, 'error': "빈 값이 있습니다."})
                post.postname = postname
                post.contents = contents
                post.save()
                if request.POST['chkimg'] == "imgchange":
                    imgs = Img.objects.filter(post_id=post)
                    for i in imgs:
                        os.remove(os.path.join(settings.MEDIA_ROOT, i.img.path))
                    imgs.delete()
                    for img in request.FILES.getlist('imgs'):
                        image = Img(post_id=post, img=img)
                        image.save()
                if request.POST['chkfile'] == "filechange":
                    files = File.objects.filter(post_id=post)
                    for i in files:
                        os.remove(os.path.join(settings.MEDIA_ROOT, i.file.path))
                    files.delete()
                    for file in request.FILES.getlist('files'):
                        f = File(post_id=post, file=file, content_type=file.content_type, name=os.path.basename(file.name))
                        f.save()
                return redirect("/post/" + str(post_id))
            else:
                return render(request, "modify.html", {'post': post, 'post_id': post_id})


def delete(request, post_id):
    post = Post.objects.get(id=post_id)
    imgs = Img.objects.filter(post_id=post)
    files = File.objects.filter(post_id=post)
    if not request.user.is_authenticated:
        return redirect("/login/")
    else:
        if post.author != request.user.get_username():
            return redirect("/post/" + str(post_id))
        else:
            for i in imgs:
                os.remove(os.path.join(settings.MEDIA_ROOT, i.img.path))
            for i in files:
                os.remove(os.path.join(settings.MEDIA_ROOT, i.file.path))
            post.delete()
            return redirect("/")


def post(request, post_id):
    post = Post.objects.get(id=post_id)
    imgs = Img.objects.filter(post_id=post)
    files = File.objects.filter(post_id=post)
    if request.method == "POST" and request.POST['submit'] == "reply":
        if not request.user.is_authenticated:
            return redirect("/login/")
        else:
            r = Reply(post_id=post, author=request.user.get_username(), contents=request.POST['contents'])
            r.save()
    reply = getReply(post_id)
    return render(request, "post.html", {'post': post, 'reply': reply, 'imgs': imgs, 'files': files})


def download(request, file_id):
    file = File.objects.get(id=file_id)
    file_path = file.file.path
    file_type = file.content_type
    filename = urllib.parse.quote(file.name.encode('utf-8'))
    fs = FileSystemStorage(file_path)
    response = FileResponse(fs.open(file_path, 'rb'), content_type=file_type)
    a = f'attachment; filename*=UTF-8\'\'%s' % filename
    response['Content-Disposition'] = a

    return response


def rd(request, reply_id):
    r = Reply.objects.get(id=reply_id)
    p_id = r.post_id
    if not request.user.is_authenticated:
        return redirect("/login/")
    else:
        if r.author != request.user.get_username():
            return redirect("/post/" + str(p_id))
        else:
            r.delete()
            return redirect("/post/" + str(p_id))


def rm(request, reply_id):
    r = Reply.objects.get(id=reply_id)
    p_id = r.post_id
    if not request.user.is_authenticated:
        return redirect("/login/")
    else:
        if r.author != request.user.get_username():
            return redirect("/post/" + str(p_id))
        else:
            r.contents = request.POST['contents']
            r.save()
            return redirect("/post/" + str(p_id))


def rr(request, reply_id):
    reply = Reply.objects.get(id=reply_id)
    post_id = reply.post_id
    if not request.user.is_authenticated:
        return redirect("/login/")
    else:
        rereply = Reply(post_id=post_id, author=request.user.get_username(), contents=request.POST['contents'], re_id=reply, depth=reply.depth+1)
        rereply.save()
    return redirect("/post/"+str(post_id))


def mypage(request):
    page = request.GET.get('page', '1')
    postlist = Post.objects.filter(author=request.user.get_username()).order_by('-c_date')
    paginator = Paginator(postlist, 5)
    page_obj = paginator.get_page(page)

    rpage = request.GET.get('rpage', '1')
    replylist = Reply.objects.filter(author=request.user.get_username()).order_by('-c_date')
    rpaginator = Paginator(replylist, 5)
    rpage_obj = rpaginator.get_page(rpage)
    context = {'postlist': page_obj, 'replylist': rpage_obj, 'page': page, 'rpage': rpage}

    return render(request, "mypage.html", context)
