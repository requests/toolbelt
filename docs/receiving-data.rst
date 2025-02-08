.. _receiving-and-handling-data:

Receiving and Handling Multipart Data
=====================================

If you need, on occasion, to build a service to receive and handle ``multipart/form-data``, 
such as an endpoint to receive data from an HTML form submission, the requests_toolbelt 
package offers the capability of decoding the inbound :class:`bytes`.
This capability is provided by the :class:`requests_toolbelt.multipart.MultipartDecoder`

MultipartDecoder
----------------
.. autoclass:: requests_toolbelt.multipart.decoder.MultipartDecoder