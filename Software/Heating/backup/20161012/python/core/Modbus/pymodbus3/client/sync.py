# -*- coding: utf-8 -*-

import socket
import serial
from pymodbus3.constants import Defaults
from pymodbus3.factory import ClientDecoder
from pymodbus3.exceptions import ParameterException
from pymodbus3.exceptions import ConnectionException
from pymodbus3.transaction import FifoTransactionManager
from pymodbus3.transaction import DictTransactionManager
from pymodbus3.transaction import ModbusSocketFramer, ModbusBinaryFramer
from pymodbus3.transaction import ModbusAsciiFramer, ModbusRtuFramer
from pymodbus3.client.common import ModbusClientMixin

# Logging
import logging
_logger = logging.getLogger(__name__)


class BaseModbusClient(ModbusClientMixin):
    """
    Interface for a modbus synchronous client. Defined here are all the
    methods for performing the related request methods.  Derived classes
    simply need to implement the transport methods and set the correct
    framer.
    """

    def __init__(self, framer, **kwargs):
        """ Initialize a client instance

        :param framer: The modbus framer implementation to use
        """
        self.framer = framer
        if isinstance(self.framer, ModbusSocketFramer):
            self.transaction = DictTransactionManager(self, **kwargs)
        else:
            self.transaction = FifoTransactionManager(self, **kwargs)

    # region Client Interface

    def connect(self):
        """ Connect to the modbus remote host

        :returns: True if connection succeeded, False otherwise
        """
        raise NotImplementedError('Method not implemented by derived class')

    def close(self):
        """ Closes the underlying socket connection
        """
        pass

    def send(self, request):
        """ Sends data on the underlying socket

        :param request: The encoded request to send
        :return: The number of bytes written
        """
        raise NotImplementedError('Method not implemented by derived class')

    def receive(self, size):
        """ Reads data from the underlying descriptor

        :param size: The number of bytes to read
        :return: The bytes read
        """
        raise NotImplementedError('Method not implemented by derived class')

    # endregion

    # region Modbus Client Methods

    def execute(self, request=None):
        """
        :param request: The request to process
        :returns: The result of the request execution
        """
        if not self.connect():
            raise ConnectionException(
                'Failed to connect[{0}]'.format(self.__str__())
            )
        return self.transaction.execute(request)

    # endregion

    # region Magic methods

    def __enter__(self):
        """ Implement the client with enter block

        :returns: The current instance of the client
        """
        if not self.connect():
            raise ConnectionException(
                'Failed to connect[{0}]'.format(self.__str__())
            )
        return self

    def __exit__(self, cls, value, traceback):
        """ Implement the client with exit block """
        self.close()

    def __str__(self):
        """ Builds a string representation of the connection

        :returns: The string representation
        """
        return 'Null Transport'

    # endregion

    pass


class ModbusTcpClient(BaseModbusClient):
    """ Implementation of a modbus tcp client
    """

    def __init__(
            self,
            host='127.0.0.1', port=Defaults.Port,
            framer=ModbusSocketFramer,
            **kwargs
    ):
        """ Initialize a client instance

        :param host: The host to connect to (default 127.0.0.1)
        :param port: The modbus port to connect to (default 502)
        :param source_address: The source address tuple to bind to
            (default ('', 0))
        :param framer: The modbus framer to use (default ModbusSocketFramer)

        .. note:: The host argument will accept ipv4 and ipv6 hosts
        """
        self.host = host
        self.port = port
        self.source_address = kwargs.get('source_address', ('', 0))
        self.socket = None
        BaseModbusClient.__init__(self, framer(ClientDecoder()), **kwargs)

    def connect(self):
        """ Connect to the modbus tcp server

        :returns: True if connection succeeded, False otherwise
        """
        if self.socket:
            return True
        try:
            address = (self.host, self.port)
            self.socket = socket.create_connection(
                address,
                timeout=Defaults.Timeout,
                source_address=self.source_address
            )
        except socket.error as msg:
            _logger.error('Connection to ({0}, {1}) failed: {2}'.format(
                self.host, self.port, msg
            ))
            self.close()
        return self.socket is not None

    def close(self):
        """ Closes the underlying socket connection
        """
        if self.socket:
            self.socket.close()
        self.socket = None

    def send(self, request):
        """ Sends data on the underlying socket

        :param request: The encoded request to send
        :return: The number of bytes written
        """
        if not self.socket:
            raise ConnectionException(self.__str__())
        if request:
            return self.socket.send(request)
        return 0

    def receive(self, size):
        """ Reads data from the underlying descriptor

        :param size: The number of bytes to read
        :return: The bytes read
        """
        if not self.socket:
            raise ConnectionException(self.__str__())
        return self.socket.recv(size)

    def __str__(self):
        """ Builds a string representation of the connection

        :returns: The string representation
        """
        return '{0}:{1}'.format(self.host, self.port)


class ModbusUdpClient(BaseModbusClient):
    """ Implementation of a modbus udp client
    """

    def __init__(
            self,
            host='127.0.0.1', port=Defaults.Port,
            framer=ModbusSocketFramer,
            **kwargs
    ):
        """ Initialize a client instance

        :param host: The host to connect to (default 127.0.0.1)
        :param port: The modbus port to connect to (default 502)
        :param framer: The modbus framer to use (default ModbusSocketFramer)
        """
        self.host = host
        self.port = port
        self.socket = None
        BaseModbusClient.__init__(self, framer(ClientDecoder()), **kwargs)

    @classmethod
    def _get_address_family(cls, address):
        """ A helper method to get the correct address family
        for a given address.

        :param address: The address to get the af for
        :returns: AF_INET for ipv4 and AF_INET6 for ipv6
        """
        try:
            socket.inet_pton(socket.AF_INET6, address)
        except socket.error:  # not a valid ipv6 address
            return socket.AF_INET
        return socket.AF_INET6

    def connect(self):
        """ Connect to the modbus tcp server

        :returns: True if connection succeeded, False otherwise
        """
        if self.socket:
            return True
        try:
            family = ModbusUdpClient._get_address_family(self.host)
            self.socket = socket.socket(family, socket.SOCK_DGRAM)
        except socket.error as ex:
            _logger.error('Unable to create udp socket ' + str(ex))
            self.close()
        return self.socket is not None

    def close(self):
        """ Closes the underlying socket connection
        """
        self.socket = None

    def send(self, request):
        """ Sends data on the underlying socket

        :param request: The encoded request to send
        :return: The number of bytes written
        """
        if not self.socket:
            raise ConnectionException(self.__str__())
        if request:
            return self.socket.sendto(request, (self.host, self.port))
        return 0

    def receive(self, size):
        """ Reads data from the underlying descriptor

        :param size: The number of bytes to read
        :return: The bytes read
        """
        if not self.socket:
            raise ConnectionException(self.__str__())
        return self.socket.recvfrom(size)[0]

    def __str__(self):
        """ Builds a string representation of the connection

        :returns: The string representation
        """
        return '{0}:{1}'.format(self.host, self.port)


class ModbusSerialClient(BaseModbusClient):
    """ Implementation of a modbus serial client
    """

    def __init__(self, method='ascii', **kwargs):
        """ Initialize a serial client instance

        The methods to connect are::

          - ascii
          - rtu
          - binary

        :param method: The method to use for connection
        :param port: The serial port to attach to
        :param stopbits: The number of stop bits to use
        :param bytesize: The bytesize of the serial messages
        :param parity: Which kind of parity to use
        :param baudrate: The baud rate to use for the serial device
        :param timeout: The timeout between serial requests (default 3s)
        """
        self.method = method
        self.socket = None
        BaseModbusClient.__init__(
            self, self.__implementation(method), **kwargs
        )

        self.port = kwargs.get('port', 0)
        self.stopbits = kwargs.get('stopbits', Defaults.Stopbits)
        self.bytesize = kwargs.get('bytesize', Defaults.Bytesize)
        self.parity = kwargs.get('parity',   Defaults.Parity)
        self.baudrate = kwargs.get('baudrate', Defaults.Baudrate)
        self.timeout = kwargs.get('timeout',  Defaults.Timeout)

    @staticmethod
    def __implementation(method):
        """ Returns the requested framer

        :method: The serial framer to instantiate
        :returns: The requested serial framer
        """
        method = method.lower()
        if method == 'ascii':
            return ModbusAsciiFramer(ClientDecoder())
        elif method == 'rtu':
            return ModbusRtuFramer(ClientDecoder())
        elif method == 'binary':
            return ModbusBinaryFramer(ClientDecoder())
        elif method == 'socket':
            return ModbusSocketFramer(ClientDecoder())
        raise ParameterException('Invalid framer method requested')

    def connect(self):
        """ Connect to the modbus serial server

        :returns: True if connection succeeded, False otherwise
        """
        if self.socket:
            return True
        try:
            self.socket = serial.Serial(
                port=self.port,
                timeout=self.timeout,
                bytesize=self.bytesize,
                stopbits=self.stopbits,
                baudrate=self.baudrate,
                parity=self.parity
            )
        except serial.SerialException as msg:
            _logger.error(msg)
            self.close()
        return self.socket is not None

    def close(self):
        """ Closes the underlying socket connection
        """
        if self.socket:
            self.socket.close()
        self.socket = None

    def send(self, request):
        """ Sends data on the underlying socket

        :param request: The encoded request to send
        :return: The number of bytes written
        """
        if not self.socket:
            raise ConnectionException(self.__str__())
        if request:
            return self.socket.write(request)
        return 0

    def receive(self, size):
        """ Reads data from the underlying descriptor

        :param size: The number of bytes to read
        :return: The bytes read
        """
        if not self.socket:
            raise ConnectionException(self.__str__())
        return self.socket.read(size)

    def __str__(self):
        """ Builds a string representation of the connection

        :returns: The string representation
        """
        return '{0} baud[{1}]'.format(self.method, self.baudrate)


# Exported symbols
__all__ = [
    'ModbusTcpClient',
    'ModbusUdpClient',
    'ModbusSerialClient'
]
