<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html class=cached><head><link rel="stylesheet" type="text/css" href="/codesearch/css/cached_page.css" /><meta http-equiv="content-type" content="text/html; charset=UTF-8"><title>GScan/gscan.py - Google Code Search</title><script type="text/javascript">
<!--
function sf(){document.getElementById("content").focus();_tabdivs = new Array();_tabdivs[0] = "filelist";_tabdivs[1] = "outline";selectTab(0);_lhl = -1;}
function sc(e) {if (e == null) {return;}var d = document.getElementById("content");d.scrollTop = e.offsetTop;}
function lh(n, f) {l = document.getElementById("l" + n);l.className = f ? "cclhl" : "";}
function slh(n) {if (_lhl != -1 && _lhl != undefined) lh(_lhl, false);_lhl = n;lh(n, true);}function scl(n) {slh(n);nl = n - 5;if (nl <= 0) nl = 1;l = document.getElementById("l" + nl);sc(l);}
var _csm,  _csn,  _lhl,  _tabdivs;
function ch() { return document.body.clientHeight; }
function cw() { return document.body.clientWidth; }
function $(id) { return document.getElementById(id); }
function gpx(id, prop) {var l = $(id).currentStyle[prop] + ""; return l.substr(0, l.length - 2) - 0; }
function vi(id) { return gpx(id, "top") + gpx(id, "bottom"); }
function hi(id) { return gpx(id, "left") + gpx(id, "right"); }
function py(obj) {obj = $(obj);var curtop = 0;while (1) {curtop += obj.offsetTop;if (!obj.offsetParent) return curtop;obj = obj.offsetParent;}}
function osf(t) {t.focused = true;}
function osb(t) {t.focused = false;}
function setCSSclass(d, c){if (d != null) {d.setAttribute("class", c); d.className = c; }}
function selectTab(id) {var i;for (i = 0; i < _tabdivs.length; i++) {var tab = document.getElementById(_tabdivs[i]);if (i != id) {setCSSclass(document.getElementById(_tabdivs[i] + "tab"), "tab");if (tab != null) {tab.style.display = "none";}} else {setCSSclass(document.getElementById(_tabdivs[i] + "tab"), "selectedtab");if (tab != null) {tab.style.display = "block";}}}}
// -->
</script><!--[if lt IE 7]><style type="text/css">
#leftpanel, #centerpanel {top:26px;bottom:4px;}
#file, #tab {height:19px;padding-top:6px;}
#license {padding-top:7px;}
#leftcontainer, #content {top:26px;}
#bluepanel {width:expression(cw()-hi("bluepanel"));
height:expression(ch()-py("bluepanel"));
}
#leftpanel, #centerpanel {height:expression(ch()-py("bluepanel")-vi("centerpanel"));}
#centerpanel {width:expression(cw()-hi("bluepanel")-hi("centerpanel"));}
#leftcontainer, #content {height:expression(ch()-py("bluepanel")-vi("centerpanel")-vi("content"));}
</style><![endif]-->
</head><body bgcolor="#ffffff" onload="sf()" class=cached><div id="cachedcopy">This is Google's cached copy of <span class=cachedlink><a href="/codesearch/url?hl=en&ct=rpc&url=http://ferraroluciano.googlecode.com/svn&usg=AFQjCNFd8x5MaB6V5-991IXjhAIMyNsBhw">http://ferraroluciano.googlecode.com/svn</a></span> &nbsp;</div><div id="logo"><div id="img"><a href="/codesearch?hl=en"><img src="http://www.google.com/intl/en/images/codesearch_logo_sm.gif" width=150 height=55 alt="" border=0></a></div><div id="input"><form method=GET action="/codesearch" name=f><input type=hidden name=hl value=en><input type=hidden name=lr value=""><input type=text name=q size=31 maxlength=2048 value="" title="Search" id=sbox onfocus="osf(this)" onblur="osb(this)"> <input type=submit name=sbtn value="Search"><font size=-2>&nbsp;&nbsp;&nbsp;<a href="/codesearch/advanced_code_search?hl=en&q=+show:PmkR6tAA1b8:itdIHyvENjI:PmkR6tAA1b8">Advanced Code Search</a></font><div><table border=0 cellpadding=1 cellspacing=0><tr valign=top><td><input type=hidden name=as_package value="http://ferraroluciano.googlecode.com/svn"><input id=all type=radio name=exact_package value="" checked></td><td><div class=labelmargin><label for=all> Search all code </label></div></td><td><input id=package type=radio name=exact_package value="1" ></td><td><div class=labelmargin><label for=package> Search in svn  </label></div></td></tr></table>&nbsp;</div></form></div> </div> <div id=loadingindicator>Loading...</div><div id=bluepanel class=cached><div id=path><a href="/codesearch?hl=en&amp;q=show:FidoFJsRih0:sntM2kbZnSg&amp;sa=N&amp;ct=rdp&amp;cs_p=http://ferraroluciano.googlecode.com/svn">http://ferraroluciano.googlecode.com/svn</a>/ GScan/</div><div id=leftpanel class=leftpanel><div class=tabpane><span id=filelisttab class=selectedtab onclick="selectTab(0);">Files</span> | <span id=outlinetab class=tab onclick="selectTab(1);">Outline</span><span class=rednewmark>New!</span></div><div id=leftcontainer><div id=filelist><pre class=dirlistpre><a href="/codesearch?hl=en&amp;q=show:3rPM40MZEvk:itdIHyvENjI:3rPM40MZEvk&amp;sa=N&amp;ct=rd&amp;cs_p=http://ferraroluciano.googlecode.com/svn&amp;cs_f=GScan/gscan.glade&amp;start=1" class="direlem">gscan.glade</a>
<b>gscan.py</b>
</pre></div><div id=outline><table border=0 cellspacing=0 cellpadding=0><tr height=20><td width=20 nowrap align=center><div class=outlineiconC>C</div></td><td nowrap colspan=2 align=left><span class=outlineelem onclick="scl(11);" align=left><b>Scan</b> <span class=outlineparam></span></span></td></tr><tr height=20><td width=20 nowrap ><div class=outlinediv1><div class=outlinediv4>&nbsp;</div>&nbsp;</div><div class=outlinediv5>&nbsp;</div></td><td width=20 nowrap align=center><div class=outlineiconM>M</div></td><td nowrap colspan=1 align=left><span class=outlineelem onclick="scl(12);" align=left><b>__init__</b> <span class=outlineparam>(self, host, ports)</span></span></td></tr><tr height=20><td width=20 nowrap ><div class=outlinediv1><div class=outlinediv4>&nbsp;</div>&nbsp;</div><div class=outlinediv6>&nbsp;</div></td><td width=20 nowrap align=center><div class=outlineiconM>M</div></td><td nowrap colspan=1 align=left><span class=outlineelem onclick="scl(17);" align=left><b>scan</b> <span class=outlineparam>(self, insert, timeout=0.1)</span></span></td></tr><tr height=20><td width=20 nowrap align=center><div class=outlineiconC>C</div></td><td nowrap colspan=2 align=left><span class=outlineelem onclick="scl(33);" align=left><b>GScan</b> <span class=outlineparam></span></span></td></tr><tr height=20><td width=20 nowrap ><div class=outlinediv1><div class=outlinediv4>&nbsp;</div>&nbsp;</div><div class=outlinediv5>&nbsp;</div></td><td width=20 nowrap align=center><div class=outlineiconM>M</div></td><td nowrap colspan=1 align=left><span class=outlineelem onclick="scl(34);" align=left><b>__init__</b> <span class=outlineparam>(self)</span></span></td></tr><tr height=20><td width=20 nowrap ><div class=outlinediv1><div class=outlinediv4>&nbsp;</div>&nbsp;</div><div class=outlinediv5>&nbsp;</div></td><td width=20 nowrap align=center><div class=outlineiconM>M</div></td><td nowrap colspan=1 align=left><span class=outlineelem onclick="scl(48);" align=left><b>connect_clicked</b> <span class=outlineparam>(self, button)</span></span></td></tr><tr height=20><td width=20 nowrap ><div class=outlinediv1><div class=outlinediv4>&nbsp;</div>&nbsp;</div><div class=outlinediv5>&nbsp;</div></td><td width=20 nowrap align=center><div class=outlineiconM>M</div></td><td nowrap colspan=1 align=left><span class=outlineelem onclick="scl(54);" align=left><b>insert</b> <span class=outlineparam>(self, text)</span></span></td></tr><tr height=20><td width=20 nowrap ><div class=outlinediv1><div class=outlinediv4>&nbsp;</div>&nbsp;</div><div class=outlinediv6>&nbsp;</div></td><td width=20 nowrap align=center><div class=outlineiconM>M</div></td><td nowrap colspan=1 align=left><span class=outlineelem onclick="scl(60);" align=left><b>start</b> <span class=outlineparam>(self)</span></span></td></tr></table></div></div> </div> <div id=centerpanel class=centerpanel><div id="file">gscan.py</div><div id="license"><span class="a">License: Unknown</span> - Python</div><div id="content"><div id="lnp"><pre>1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
56
57
58
59
60
61
62
63
64
65
66
67
68
69
70
71
</pre></div><div id="code"><pre><a name=first></a><span id=l1>import <a href="/codesearch?hl=en&q=file:(/%7C%5E)thread(/__init__)%3F%5C.py%24&as_package=http://ferraroluciano.googlecode.com/svn&is_navigation=1">thread</a>
</span><span id=l2>import <a href="/codesearch?hl=en&q=file:(/%7C%5E)socket(/__init__)%3F%5C.py%24&as_package=http://ferraroluciano.googlecode.com/svn&is_navigation=1">socket</a>
</span><span id=l3>
</span><span id=l4>import <a href="/codesearch?hl=en&q=file:(/%7C%5E)pygtk(/__init__)%3F%5C.py%24&as_package=http://ferraroluciano.googlecode.com/svn&is_navigation=1">pygtk</a>
</span><span id=l5>pygtk.require(&quot;2.0&quot;)
</span><span id=l6>import <a href="/codesearch?hl=en&q=file:(/%7C%5E)gtk(/__init__)%3F%5C.py%24&as_package=http://ferraroluciano.googlecode.com/svn&is_navigation=1">gtk</a>
</span><span id=l7>import <a href="/codesearch?hl=en&q=file:(/%7C%5E)gtk/glade(/__init__)%3F%5C.py%24&as_package=http://ferraroluciano.googlecode.com/svn&is_navigation=1">gtk.glade</a>
</span><span id=l8>
</span><span id=l9>gtk.gdk.threads_init()
</span><span id=l10>
</span><span id=l11>class Scan:
</span><span id=l12>    def __init__(self, host, ports):
</span><span id=l13>        self.host, self.ports = host, ports
</span><span id=l14>
</span><span id=l15>        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
</span><span id=l16>
</span><span id=l17>    def scan(self, insert, timeout=0.1):
</span><span id=l18>        result = {}
</span><span id=l19>        self.socket.settimeout(timeout)
</span><span id=l20>        insert(&quot;&#92;n* SCANNING %s (%s) *&#92;n&#92;n&quot; % (
</span><span id=l21>                self.host, str(self.ports[0])+&quot;-&quot;+str(self.ports[-1])))
</span><span id=l22>
</span><span id=l23>        for port in self.ports:
</span><span id=l24>            insert(str(port) + &quot;: &quot;)
</span><span id=l25>            try:
</span><span id=l26>                self.socket.connect((self.host, port))
</span><span id=l27>                result[port] = True
</span><span id=l28>                insert(&quot;CLOSED&#92;n&quot;)
</span><span id=l29>            except:
</span><span id=l30>                result[port] = False
</span><span id=l31>                insert(&quot;OPEN!&#92;n&quot;)
</span><span id=l32>
</span><span id=l33>class GScan:
</span><span id=l34>    def __init__(self):
</span><span id=l35>        self.root = gtk.glade.XML(&quot;gscan.glade&quot;)
</span><span id=l36>
</span><span id=l37>        widgets = [&quot;window&quot;, &quot;textview&quot;, &quot;scrolled&quot;, &quot;statusbar&quot;,
</span><span id=l38>                   &quot;port&quot;, &quot;host&quot;, &quot;connect&quot;]
</span><span id=l39>        for widget in widgets:
</span><span id=l40>            setattr(self, widget, self.root.get_widget(widget))
</span><span id=l41>
</span><span id=l42>        self.signals = {
</span><span id=l43>            &quot;on_window_destroy&quot;:lambda x: gtk.main_quit,
</span><span id=l44>            &quot;on_connect_clicked&quot;:self.connect_clicked
</span><span id=l45>            }
</span><span id=l46>        self.root.signal_autoconnect(self.signals)
</span><span id=l47>
</span><span id=l48>    def connect_clicked(self, button):
</span><span id=l49>        ports = [int(x) for x in self.port.get_text().split(&quot;-&quot;)]
</span><span id=l50>        scanner = Scan(self.host.get_text(), range(ports[0], ports[1]+1))
</span><span id=l51>        thread.start_new_thread(scanner.scan, (self.insert,))
</span><span id=l52>        <span class=cc>#scanner.scan(self.insert)</span>
</span><span id=l53>
</span><span id=l54>    def insert(self, text):
</span><span id=l55>        textbuffer = self.textview.get_buffer()
</span><span id=l56>        textbuffer.insert(textbuffer.get_end_iter(), text)
</span><span id=l57>
</span><span id=l58>        self.scrolled.emit('scroll-child', gtk.SCROLL_END, False)
</span><span id=l59>
</span><span id=l60>    def start(self):
</span><span id=l61>        self.window.show_all()
</span><span id=l62>
</span><span id=l63>if __name__ != &quot;__main__&quot;:
</span><span id=l64>    raise SystemExit
</span><span id=l65>
</span><span id=l66>gtk.gdk.threads_enter()
</span><span id=l67>gs = GScan()
</span><span id=l68>gs.start()
</span><span id=l69>
</span><span id=l70>gtk.main()
</span><span id=l71>gtk.gdk.threads_leave()
</span></pre></div></div></div> </div> </body></html>