django-aliyun-oss
=================

Django backends storages for Aliyun OSS

嵌入了Aliyun OSS Python SDK开发包 0.3.2
=================
Settings

DEFAULT_FILE_STORAGE = 'aliyun_oss.backends.oss.OSSStorage'

OSS_ACCESS_URL ＝ 阿里云存储访问地址 
	杭州节点外网：oss.aliyuncs.com
	            oss-cn-hangzhou.aliyuncs.com
	青岛节点外网：oss-cn-qingdao.aliyuncs.com
	杭州节点内网：oss-internal.aliyuncs.com   
	            oss-cn-hangzhou-internal.aliyuncs.com
	青岛节点内网：oss-cn-qingdao-internal.aliyuncs.com

OSS_ACCESS_KEY_ID  阿里云OSS KeyID  String类型

OSS_SECRET_ACCESS_KEY     OSS Secret  String类型

OSS_STORAGE_BUCKET_NAME   BUCKET名


OSS_HEADERS(optional)  公共Response HEADER 
<pre>
OSS_HEADERS = {
    'Cache-Control': 'max-age=31536000',
}
</pre>

OSS_DEFAULT_ACL（optional） 文件访问权限 默认 'public-read'




