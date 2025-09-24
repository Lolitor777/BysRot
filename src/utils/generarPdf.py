
from PyQt6.QtPrintSupport import QPrinter
from PyQt6.QtGui import QPainter, QPageSize, QRegion
from PyQt6.QtCore import QRect, QPoint, Qt

def generar_pdf(ruta, rotulos):
   
    if not rotulos:
        return
    
    printer = QPrinter(QPrinter.PrinterMode.HighResolution)
    printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
    printer.setOutputFileName(ruta)
    printer.setPageSize(QPageSize(QPageSize.PageSizeId.Letter))
    printer.setFullPage(True)
    printer.setResolution(300)  

    painter = QPainter()
    if not painter.begin(printer):
        return False

    page_rect = printer.pageRect(QPrinter.Unit.DevicePixel)
    
    cols, rows = 2, 4
    
    
    margin = 20 
    usable_width = page_rect.width() - (2 * margin)
    usable_height = page_rect.height() - (2 * margin)
    
    # Dimensiones de cada celda
    cell_width = usable_width / cols
    cell_height = usable_height / rows
    
    for i, rotulo in enumerate(rotulos):
        # Calculamos posición en el grid
        col = i % cols
        row = (i // cols) % rows

        # Nueva página si es necesario
        if i > 0 and i % (cols * rows) == 0:
            printer.newPage()

        # Guardamos el estado del painter
        painter.save()

        # Calculamos la posición de la celda
        x = margin + col * cell_width
        y = margin + row * cell_height
        
        # Definimos el rectángulo de destino
        target_rect = QRect(int(x), int(y), int(cell_width), int(cell_height))
        
        # Obtenemos el rectángulo del rótulo
        source_rect = rotulo.rect()
        
        # Configuramos la región de recorte para evitar superposiciones
        painter.setClipRect(target_rect)
        
        # Trasladamos al origen de la celda
        painter.translate(x, y)
        
        # Calculamos el factor de escala manteniendo proporción
        if source_rect.width() > 0 and source_rect.height() > 0:
            scale_x = cell_width / source_rect.width()
            scale_y = cell_height / source_rect.height()
            
            # Usamos el menor factor para mantener proporción
            scale = min(scale_x, scale_y) * 0.95  # 0.95 para dejar un pequeño margen
            
            # Centramos el rótulo en la celda si es necesario
            scaled_width = source_rect.width() * scale
            scaled_height = source_rect.height() * scale
            
            offset_x = (cell_width - scaled_width) / 2
            offset_y = (cell_height - scaled_height) / 2
            
            painter.translate(offset_x, offset_y)
            painter.scale(scale, scale)

        if hasattr(rotulo, "checkSyncDate"):
            rotulo.checkSyncDate.hide()

        if hasattr(rotulo, "btnDelete"):
            rotulo.btnDelete.hide()
        
        rotulo.render(painter, QPoint(0, 0), QRegion(source_rect))
        
        if hasattr(rotulo, "checkSyncDate"):
            rotulo.checkSyncDate.show()

        if hasattr(rotulo, "btnDelete"):
            rotulo.btnDelete.show()
            
        painter.restore()

    painter.end()
    return True
