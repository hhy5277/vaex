from qt import *
import numpy as np
import matplotlib.cm

import gavifast

class HistogramAndTransfer(QtGui.QWidget):
	def __init__(self, parent, colormap, function_count=3):
		super(HistogramAndTransfer, self).__init__(parent)
		self.colormap = colormap
		self.grid = None
		self.setMinimumHeight(32+100)
		self.function_count = function_count
		self.function_opacities = [0.1/2**(function_count-1-k) for k in range(function_count)] 
		self.function_sigmas = [0.05] * function_count
		self.function_means = (np.arange(function_count) / float(function_count-1)) * 0.8 + 0.10
		
		
	def paintEvent(self, event):
		painter = QtGui.QPainter()
		painter.begin(self)
		painter.fillRect(event.rect(), QtGui.QBrush(QtCore.Qt.black))
		
		self.draw_colormap(painter)
		if self.grid is not None:
			self.draw_histogram(painter)
		painter.end()
		
		
	def draw_histogram(self, painter):
		return
		grid1d = np.log10(self.grid.sum(axis=1).sum(axis=0).reshape(-1).astype(np.float64)+1)
		grid1d = np.log10(self.grid.reshape(-1).astype(np.float64)+1)
		xmin, xmax = grid1d.min(), grid1d.max()
		width = self.width()
		counts = np.zeros(width, dtype=np.float64)
		gavifast.histogram1d(grid1d, None, counts, xmin, xmax+1)
		#counts, _ = np.histogram(grid1d, bins=width, range=(xmin, xmax))
		print "histogram", xmin, xmax, counts, grid1d.mean(), len(grid1d)
		counts = np.log10(counts+1)
		counts -= counts.min()
		counts /= counts.max()
		counts *= 100
		painter.setPen(QtCore.Qt.white)
		for i in range(width):
			painter.drawLine(i, 100, i, 100-counts[i])
			
		
	def draw_colormap(self, painter):
		mapping = matplotlib.cm.ScalarMappable(cmap=self.colormap)
		rect = self.size()
		Nx, Ny = rect.width(), 32
		x = -np.arange(Nx) # TODO why are the colors reversed?
		x = np.vstack([x]*Ny)
		
		rgba = mapping.to_rgba(x, bytes=True)
		if 0:
			r, g, b, a = rgba = rgba.reshape((4,-1))
			r = r * 1
			g = g * 1
			b = b * 1
			#rgba.reshape(4,-1)[2] = r
			#rgba.reshape(4,-1)[1] = g
			#rgba.reshape(4,-1)[0] = b
			print rgba.shape, rgba.min(), rgba.max()
			
			#image = pixmap.toImage()
			rgba = np.ascontiguousarray((rgba*255.).astype(np.uint8)).astype(np.uint8)
		stringdata = rgba.tostring()
		image = QtGui.QImage(stringdata, Nx, Ny, Nx*4, QtGui.QImage.Format_RGB32)
		#pixmap = QtGui.QPixmap(Nx, Ny)
		#pixmap.convertFromImage(image)
		point = QtCore.QPoint(0, rect.height()-32)
		painter.drawImage(point, image)
		
		painter.setPen(QtCore.Qt.white)
		for i in range(self.function_count):
			x = np.arange(Nx)
			nx = x / (Nx-1.)
			y = np.exp(-((nx-self.function_means[i])/self.function_sigmas[i])**2) * (np.log10(self.function_opacities[i])+3)/3 * 32.
			x = x.astype(np.int32)
			y = 100+32-y.astype(np.int32)
			polygon = QtGui.QPolygon(map(lambda x: QtCore.QPoint(*x), zip(x, y)))
			painter.drawPolyline(polygon)
		

		