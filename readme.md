# WPS-Zotero

A WPS Writer addon for integrating Zotero on Linux. WPS is an office suite with excellent compatiblity to MS Word. For scientific workers to migrate from Windows to GNU/Linux, a good Word processor with citation management support has always been a great obstacle. With this addon, you can add/edit citations in documents created with MS Word and send your documents created with WPS Writer to others to edit in MS Word. By design, it should provide a seamless experience for people who work in an environment where everyone else use Windows and MS Word. If you encountered any trouble, please open an issue, I will fix it ASAP.

这个插件可以让你在Linux下写论文，再发给别人在Windows/MS Word下改，两边插入的引用可以共通（需要选择将引用存储为域），喜欢的朋友点个星星，帮忙散播一下消息，帮助更多科研狗逃脱Windows/MS Office！

## Installation

Install WPS and Zotero first.

Download the repo, go into it, and issue `./install.sh`. The script will try to install python package `requests` for you if you don't already have it. Should that fail, you should install it manually and you may have to change the pip source.

To uninstall, run `./uninstall.sh`.

直接下载源码或release包解压，cd进去执行install.sh即可，这个插件需要python的requests包，如果自动安装不行就自己手动安装，有些网络环境可能要换个pip源，比如ustc的源。卸载就运行uninstal.sh即可。

## How does it work

This addon uses WPS's jsapi to operate in WPS Writer, and manage citation using Zotero's [HTTP citing protocol](https://www.zotero.org/support/dev/client_coding/http_integration_protocol). Due to the host permissions, direct http requests from the client will be blocked by CORS. As a workaround, the requests are made with an external python script (agent.py). The data transfer between the client and the agent is done by named pipes.

## About MS Word compatibility

The addon will store data to documents in a way similar as MS Word. The only difference is that the `formattedCitation` in the field data is in XML format, while MS Word uses RTF format. However, this shouldn't pose any inconvenience for common users. Because Zotero will automatically update it for you. However, you should always store citations in fields rather than bookmarks, as the later is not supported in this addon.

## Common fixes

If there's something wrong occured during a transaction, the Zotero server will then be unusable, you will then be advised to restart Zotero. For other cases, restart WPS Writer and Zotero to see if the problem persists. If so, delete the pipe and pid file located in ~/.wps-zotero.

## Windows support

Windows support should be out of box if there's no host permission restrictions on Zotero's connector server. To make this work on Windows would require another workaround approach other than `mkfifo`, a http proxy maybe. Anyway, it's planned and will be implemented in the future.

暂时只能在Linux用，因为用了FIFO，后期将会支持Windows。动手能力强的朋友可以开个反CORS代理，改zclient.js里的postRequest函数，把URL用代理地址代替，用原生方法发起http请求。

## Citation formatting

The client only supports a limited set of formatting tags (\<p\>, \<br\>, \<b\>, \<i\> ...), which should cover all using cases. However, if you found any formating problems, please raise an issue, I will add it.
