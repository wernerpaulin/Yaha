<?xml version="1.0" encoding="UTF-8"?>

<xsl:stylesheet version="1.0"
 xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:template match="/">
   <html>
   <body style="font-family:arial;">
   <h2>Yaha Receipe Data</h2>
   <table border="1">
     <tr bgcolor="#FF8800">
       <th>Process Tag</th>
       <th>UI Tag</th>
       <th>Value Type</th>
       <th>Value REAL</th>
       <th>Value TEXT</th>
     </tr>
     <xsl:for-each select="pdi/process_data">
     <tr>
       <td><xsl:value-of select="processTag"/></td>
       <td><xsl:value-of select="uiTag"/></td>
       <td><xsl:value-of select="valueType"/></td>
       <td><xsl:value-of select="valueREAL"/></td>
       <td><xsl:value-of select="valueTEXT"/></td>
     </tr>
     </xsl:for-each>
   </table>
   </body>
   </html>
</xsl:template>

</xsl:stylesheet>
