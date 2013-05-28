#!/usr/bin/env python
"""
Created on 23 janv. 2013

A quick'n'dirty script to grab images from http devices that stream jpeg in
a parallel way.

@author: mutah
"""
import sys
import os
import optparse
import datetime
import urllib2
import urlparse
import multiprocessing

#############################################################################
class GrabWorker(multiprocessing.Process):
    """A process that grabs an image from a http device."""
    
    #########################################################################
    def __init__(self, queue, options):
        """
        constructor
        
        @param queue: a queue filled by the parent with url links
        """
        super(GrabWorker, self).__init__()
        self.queue = queue
        self.options = options
    
    #########################################################################
    def run(self):
        """
        reads links in the queue and process the image grab until None is
        received (sentinel argument of iter())
        """
        for link in iter(self.queue.get, None):
            print "getting", link
                        
            img_data = self.grab_image(link)
            
            if img_data:
                filename = self.generate_path(link)
                print "saving ", filename 
                open(filename, "wb").write(img_data)
            else:
                sys.stderr.write("failed  : " + link + os.linesep)
                open("fail.log", "a+").write(link + os.linesep)
                
    #########################################################################
    def generate_path(self, link):
        """
        generates a path for an url and also creates the directory on the
        file system for the target file
        
        @param link: a link to a jpeg stream        
        @return: the generated path for an image
        """
        pu = urlparse.urlparse(link)
        host = pu.netloc.split(":")[0].replace(".", "_")        
        now = datetime.datetime.now()
        
        filename = "%s_%d_%02d_%02d_%02d_%02d.jpg" % (
            host, now.year, now.month, now.day, now.hour, now.minute
            )
        subdir = os.path.join(self.options.output, host)
        
        for path in (self.options.output, subdir):
            if not os.path.isdir(path):
                os.mkdir(path)        
        return os.path.join(subdir, filename)

    #########################################################################
    def grab_image(self, link):
        """
        fetches an image from internet !
        
        @param link: a link to a jpeg stream
        @return: jpeg data or None if no image was found
        """
        # opens the link
        try:
            url = urllib2.urlopen(link)
        except IOError, e:
            sys.stderr.write(link + " IOError : " + str(e).strip() + os.linesep)
            return
        except urllib2.httplib.BadStatusLine, e:
            sys.stderr.write(link + " : bad status " + str(e).strip() + os.linesep)
            return
        
        frame_found = False
        img_buffer = []
        img_size = 0
        img_read = 0
        buff_size = 1024  # WARNING Magic Number !
        
        while not frame_found:            
            data = url.read(buff_size)
            if not data:
                break
            
            if img_size:
                if img_read >= img_size:
                    frame_found = True
                else: 
                    if img_read + buff_size >= img_size:
                        buff_size = img_size - img_read
                img_buffer.append(data)
                img_read += len(data)
            else:
                if '\r\n\r\n' in data:                    
                    data_start = 0        
                    for line in data.splitlines():
                        
                        if line.startswith("Content-Length:"):
                            img_size = int(line.split(":")[1])
                                                        
                        if img_size and not line:
                            data_start = data_start + 2  # WARNING Magic Number !
                            break
                                                    
                        data_start += len(line) + 2  # WARNING Magic Number !
                            
                    if img_size:
                        img_buffer.append(data[data_start:])
                        img_read += len(img_buffer[0])
        
        if frame_found:
            return "".join(img_buffer)        

#############################################################################
def main():
    parser = optparse.OptionParser()    
    parser.add_option("-i", "--input",
                      help="path to a file containing one url per line",
                      )
    
    parser.add_option("-o", "--output", help="output directory",
                      default="img"
                      )
        
    parser.add_option("-p", "--parallel", help="number of subprocesses.\
Don't hesitate to try high values like 64 or 128 ;)",
                      action='store', type='int',
                      default=multiprocessing.cpu_count() * 4,
                      )
    
    (options, _) = parser.parse_args()
    
    if not options.input:
        parser.print_help()
        sys.stderr.write("no input. use -i filename" + os.linesep)
        sys.exit(1)
        
    request_queue = multiprocessing.Queue()

    for _ in xrange(options.parallel):
        GrabWorker(request_queue, options).start()
    
    for link in open(options.input):
        link = link.strip() 
        if link:
            request_queue.put(link)    
    
    for _ in xrange(options.parallel):
        request_queue.put(None) 


#############################################################################
if __name__ == '__main__':        
    main()
