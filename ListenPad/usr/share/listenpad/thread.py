import time

import threading, thread
import gobject, gtk

gtk.gdk.threads_init()


class GeneratorTask(object):

   def __init__(self, generator, loop_callback, complete_callback=None):
       self.generator = generator
       self.loop_callback = loop_callback
       self.complete_callback = complete_callback

   def _start(self, *args, **kwargs):
       self._stopped = False
       for ret in self.generator(*args, **kwargs):
           if self._stopped:
               thread.exit()
           gobject.idle_add(self._loop, ret)
       if self.complete_callback is not None:
           gobject.idle_add(self.complete_callback)

   def _loop(self, ret):
       if ret is None:
           ret = ()
       if not isinstance(ret, tuple):
           ret = (ret,)
       self.loop_callback(*ret)

   def start(self, *args, **kwargs):
       threading.Thread(target=self._start, args=args, kwargs=kwargs).start()

   def stop(self):
       self._stopped = True

class MainWindow(gtk.Window):
   def __init__(self):
       super(MainWindow, self).__init__()
       vb = gtk.VBox()
       self.add(vb)
       self.progress_bar = gtk.ProgressBar()
       vb.pack_start(self.progress_bar)
       b = gtk.Button(stock=gtk.STOCK_OK)
       vb.pack_start(b)
       b.connect('clicked', self.on_button_clicked)
       self.show_all()

   def on_button_clicked(self, button):
       GeneratorTask(self.count_up,
                     self.set_progress_bar_fraction).start(5)

   def count_up(self, maximum):
       for i in xrange(maximum):
           fraction = (i + 1) / float(maximum)
           time.sleep(1)
           yield fraction

   def set_progress_bar_fraction(self, fraction):
       self.progress_bar.set_fraction(fraction)

w = MainWindow()
gtk.main()
