<?xml version="1.0" encoding="UTF-8"?>

<xsl:stylesheet version="1.0"
 xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:template match="/">
   <html>
   <body style="font-family:arial;">
   <h2>Yaha Process Data Image</h2>
   <table border="1">
     <tr bgcolor="#FF8800">
       <th>Process Tag</th>
       <th>UI Tag</th>
       <th>Value Type</th>
       <th>Value REAL</th>
       <th>Value TEXT</th>
       <th>Domain</th>
       <th>Owner</th>
       <th>Device ID</th>
       <th>UI Mode</th>
       <th>Low REAL</th>
       <th>High REAL</th>
       <th>Zone</th>
       <th>Subzone</th>
       <th>Room</th>
       <th>IO Type</th>
     </tr>
     <xsl:for-each select="pdi/process_data">
     <tr>
       <td><xsl:value-of select="processTag"/></td>
       <td><xsl:value-of select="uiTag"/></td>
       <td><xsl:value-of select="valueType"/></td>
       <td><xsl:value-of select="valueREAL"/></td>
       <td><xsl:value-of select="valueTEXT"/></td>
       <td><xsl:value-of select="domain"/></td>
       <td><xsl:value-of select="owner"/></td>
       <td><xsl:value-of select="deviceID"/></td>
       <td><xsl:value-of select="uiMode"/></td>
       <td><xsl:value-of select="lowREAL"/></td>
       <td><xsl:value-of select="highREAL"/></td>
       <td><xsl:value-of select="zone"/></td>
       <td><xsl:value-of select="subzone"/></td>
       <td><xsl:value-of select="room"/></td>
       <td><xsl:value-of select="ioType"/></td>
     </tr>
     </xsl:for-each>
   </table>
   </body>
   </html>
</xsl:template>

</xsl:stylesheet>
