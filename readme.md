# WPS-Zotero

A WPS Writer add-on for integrating with Zotero. **It supports both GNU/Linux and Windows now**. WPS is an office suite with excellent compatibility to MS Word. For scientific workers to migrate from Windows to GNU/Linux, lacking a good Word processor with citation management support has always been a great obstacle. With this add-on, you can add/edit citations in documents created with MS Word or send your documents created with WPS Writer to others to edit in MS Word. It should provide a seamless experience for people who work in an environment where everyone else use Windows and MS Word. If you encountered any problem, please open an issue, I will fix it ASAP.

这个插件可以让你在Linux下写论文，再发给别人在Windows/MS Word下改，两边插入的引用可以共通（需要选择将引用存储为域）。**现在也支持Windows了哦**。喜欢的朋友点个星星，帮忙散播一下消息，帮助更多科研狗逃脱Windows/MS Office！

## Installation

Install the latest version of WPS and Zotero first. Make sure you have Python3 installed.

Download **the repository** (release packages are older and therefore not recommended), unzip and go into it, and run `./install.py` (`python.exe install.py` on Windows).

To uninstall, run `./install.py -u` (`python.exe install.py -u` on Windows).

(On Windows, you can open a terminal by hitting the start button and type `cmd`, then use `cd` command to go to the unzipped directory, `cd D:\Downloads\WPS-Zotero`, e.g.)

直接下载源码包解压，Linux用户执行install.py安装；Windows用户双击bat安装脚本进行安装或卸载，如果不行可以用另一种方法安装，看[**详细教程**](https://www.cnblogs.com/tkwblog/articles/17705935.html)。

## How does it work

This add-on uses WPS's jsapi to control WPS Writer, and works with Zotero through its [HTTP citing protocol](https://www.zotero.org/support/dev/client_coding/http_integration_protocol). Due to [the host permission restrictions of Zotero](https://groups.google.com/g/zotero-dev/c/MjWzJxaVoSs), direct HTTP requests from the client will be blocked by CORS. As a workaround, a simple HTTP proxy written in Python is used.

## About MS Word compatibility

The add-on will store data to documents in a way similar as MS Word does. The only difference is that the `formattedCitation` in the field data is in XML format, while MS Word uses RTF format. However, this shouldn't pose any inconvenience for common users. Because Zotero will automatically update it for you. However, you should always store citations in fields rather than bookmarks, as the latter is not supported by this add-on.

## Common fixes

If there's something wrong occurred during a transaction, the Zotero server will then be unusable, you will then be advised to restart Zotero. For other cases, restart WPS Writer and Zotero to see if the problem persists. If the problem persists, you can run `python proxy.py kill` in the package directory to quit the proxy server manually before restarting the applications. Re-installation can be tried of course if you still can't fix it.

## Known issues

- On Windows, the Zotero citation windows might not be focused sometimes and they might be placed in background, you can click the Zotero icon on your task bar to bring it to front. This seems to be [a bug of Zotero](https://github.com/zotero/zotero-libreoffice-integration/issues/41).

- On Windows, the `ApplicationQuit` event of WPS can not be received by the add-on, so the proxy server cannot be shutdown, but this won't affect common usage and only eats a small amount of resources.
