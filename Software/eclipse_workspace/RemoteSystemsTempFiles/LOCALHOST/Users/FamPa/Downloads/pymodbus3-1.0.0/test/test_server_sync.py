import unittest
from mock import patch, Mock
import SocketServer
import serial
import socket
from pymodbus3.device import ModbusDeviceIdentification
from pymodbus3.server.sync import ModbusBaseRequestHandler
from pymodbus3.server.sync import ModbusSingleRequestHandler
from pymodbus3.server.sync import ModbusConnectedRequestHandler
from pymodbus3.server.sync import ModbusDisconnectedRequestHandler
from pymodbus3.server.sync import ModbusTcpServer, ModbusUdpServer, ModbusSerialServer
from pymodbus3.server.sync import StartTcpServer, StartUdpServer, StartSerialServer
from pymodbus3.bit_read_message import ReadCoilsRequest, ReadCoilsResponse

#---------------------------------------------------------------------------#
# Mock Classes
#---------------------------------------------------------------------------#


class MockServer(object):
    def __init__(self):
        self.framer = lambda _: "framer"
        self.decoder = "decoder"
        self.threads = []
        self.context = {}

#---------------------------------------------------------------------------#
# Fixture
#---------------------------------------------------------------------------#


class SynchronousServerTest(unittest.TestCase):
    """
    This is the unittest for the pymodbus3.server.sync module
    """

    #-----------------------------------------------------------------------#
    # Test Base Request Handler
    #-----------------------------------------------------------------------#

    def test_base_handler_undefined_methods(self):
        """ Test the base handler undefined methods"""
        handler = SocketServer.BaseRequestHandler(None, None, None)
        handler.__class__ = ModbusBaseRequestHandler
        self.assertRaises(NotImplementedError, lambda: handler.send(None))
        self.assertRaises(NotImplementedError, lambda: handler.handle())

    def test_base_handler_methods(self):
        """ Test the base class for all the clients """
        request = ReadCoilsRequest(1, 1)
        address = ('server', 12345)
        server = MockServer()
        with patch.object(ModbusBaseRequestHandler, 'handle') as mock_handle:
            with patch.object(ModbusBaseRequestHandler, 'send') as mock_send:
                mock_handle.return_value = True
                mock_send.return_value = True
                handler = ModbusBaseRequestHandler(request, address, server)
                self.assertEqual(handler.running, True)
                self.assertEqual(handler.framer, 'framer')

                handler.execute(request)
                self.assertEqual(mock_send.call_count, 1)

                server.context[0x00] = object()
                handler.execute(request)
                self.assertEqual(mock_send.call_count, 2)

    #-----------------------------------------------------------------------#
    # Test Single Request Handler
    #-----------------------------------------------------------------------#
    def test_modbus_single_request_handler_send(self):
        handler = SocketServer.BaseRequestHandler(None, None, None)
        handler.__class__ = ModbusSingleRequestHandler
        handler.framer = Mock()
        handler.framer.buildPacket.return_value = "message"
        handler.request = Mock()
        request = ReadCoilsResponse([1])
        handler.send(request)
        self.assertEqual(handler.request.send.call_count, 1)

        request.should_respond = False
        handler.send(request)
        self.assertEqual(handler.request.send.call_count, 1)

    def test_modbus_single_request_handler_handle(self):
        handler = SocketServer.BaseRequestHandler(None, None, None)
        handler.__class__ = ModbusSingleRequestHandler
        handler.framer = Mock()
        handler.framer.buildPacket.return_value = "message"
        handler.request = Mock()
        handler.request.recv.return_value = "\x12\x34"
        # exit if we are not running
        handler.running = False
        handler.handle()
        self.assertEqual(handler.framer.processIncomingPacket.call_count, 0)

        # run forever if we are running
        def _callback1(a, b):
            handler.running = False  # stop infinite loop
        handler.framer.processIncomingPacket.side_effect = _callback1
        handler.running = True
        handler.handle()
        self.assertEqual(handler.framer.processIncomingPacket.call_count, 1)

        # exceptions are simply ignored
        def _callback2(a, b):
            if handler.framer.processIncomingPacket.call_count == 2:
                raise Exception("example exception")
            else:
                handler.running = False  # stop infinite loop
        handler.framer.processIncomingPacket.side_effect = _callback2
        handler.running = True
        handler.handle()
        self.assertEqual(handler.framer.processIncomingPacket.call_count, 3)

    #-----------------------------------------------------------------------#
    # Test Connected Request Handler
    #-----------------------------------------------------------------------#
    def test_modbus_connected_request_handler_send(self):
        handler = SocketServer.BaseRequestHandler(None, None, None)
        handler.__class__ = ModbusConnectedRequestHandler
        handler.framer = Mock()
        handler.framer.buildPacket.return_value = "message"
        handler.request = Mock()
        request = ReadCoilsResponse([1])
        handler.send(request)
        self.assertEqual(handler.request.send.call_count, 1)

        request.should_respond = False
        handler.send(request)
        self.assertEqual(handler.request.send.call_count, 1)

    def test_modbus_connected_request_handler_handle(self):
        handler = SocketServer.BaseRequestHandler(None, None, None)
        handler.__class__ = ModbusConnectedRequestHandler
        handler.framer = Mock()
        handler.framer.buildPacket.return_value = "message"
        handler.request = Mock()
        handler.request.recv.return_value = "\x12\x34"

        # exit if we are not running
        handler.running = False
        handler.handle()
        self.assertEqual(handler.framer.processIncomingPacket.call_count, 0)

        # run forever if we are running
        def _callback(a, b):
            handler.running = False  # stop infinite loop
        handler.framer.processIncomingPacket.side_effect = _callback
        handler.running = True
        handler.handle()
        self.assertEqual(handler.framer.processIncomingPacket.call_count, 1)

        # socket errors cause the client to disconnect
        handler.framer.processIncomingPacket.side_effect = socket.error()
        handler.running = True
        handler.handle()
        self.assertEqual(handler.framer.processIncomingPacket.call_count, 2)

        # every other exception causes the client to disconnect
        handler.framer.processIncomingPacket.side_effect = Exception()
        handler.running = True
        handler.handle()
        self.assertEqual(handler.framer.processIncomingPacket.call_count, 3)

        # receiving no data causes the client to disconnect
        handler.request.recv.return_value = None
        handler.running = True
        handler.handle()
        self.assertEqual(handler.framer.processIncomingPacket.call_count, 3)

    #-----------------------------------------------------------------------#
    # Test Disconnected Request Handler
    #-----------------------------------------------------------------------#
    def test_modbus_disconnected_request_handler_send(self):
        handler = SocketServer.BaseRequestHandler(None, None, None)
        handler.__class__ = ModbusDisconnectedRequestHandler
        handler.framer = Mock()
        handler.framer.buildPacket.return_value = "message"
        handler.request = Mock()
        request = ReadCoilsResponse([1])
        handler.send(request)
        self.assertEqual(handler.request.sendto.call_count, 1)

        request.should_respond = False
        handler.send(request)
        self.assertEqual(handler.request.sendto.call_count, 1)

    def test_modbus_disconnected_request_handler_handle(self):
        handler = SocketServer.BaseRequestHandler(None, None, None)
        handler.__class__ = ModbusDisconnectedRequestHandler
        handler.framer = Mock()
        handler.framer.buildPacket.return_value = "message"
        handler.request = ("\x12\x34", handler.request)

        # exit if we are not running
        handler.running = False
        handler.handle()
        self.assertEqual(handler.framer.processIncomingPacket.call_count, 0)

        # run forever if we are running
        def _callback(a, b):
            handler.running = False  # stop infinite loop
        handler.framer.processIncomingPacket.side_effect = _callback
        handler.running = True
        handler.handle()
        self.assertEqual(handler.framer.processIncomingPacket.call_count, 1)

        # socket errors cause the client to disconnect
        handler.request = ("\x12\x34", handler.request)
        handler.framer.processIncomingPacket.side_effect = socket.error()
        handler.running = True
        handler.handle()
        self.assertEqual(handler.framer.processIncomingPacket.call_count, 2)

        # every other exception causes the client to disconnect
        handler.request = ("\x12\x34", handler.request)
        handler.framer.processIncomingPacket.side_effect = Exception()
        handler.running = True
        handler.handle()
        self.assertEqual(handler.framer.processIncomingPacket.call_count, 3)

        # receiving no data causes the client to disconnect
        handler.request = (None, handler.request)
        handler.running = True
        handler.handle()
        self.assertEqual(handler.framer.processIncomingPacket.call_count, 3)

    #-----------------------------------------------------------------------#
    # Test TCP Server
    #-----------------------------------------------------------------------#
    def test_tcp_server_close(self):
        """ test that the synchronous TCP server closes correctly """
        with patch.object(socket.socket, 'bind') as mock_socket:
            identity = ModbusDeviceIdentification(info={0x00: 'VendorName'})
            server = ModbusTcpServer(context=None, identity=identity)
            server.threads.append(Mock(**{'running': True}))
            server.server_close()
            self.assertEqual(server.control.Identity.VendorName, 'VendorName')
            self.assertFalse(server.threads[0].running)

    def test_tcp_server_process(self):
        """ test that the synchronous TCP server processes requests """
        with patch('SocketServer.ThreadingTCPServer') as mock_server:
            server = ModbusTcpServer(None)
            server.process_request('request', 'client')
            self.assertTrue(mock_server.process_request.called)

    #-----------------------------------------------------------------------#
    # Test UDP Server
    #-----------------------------------------------------------------------#
    def test_udp_server_close(self):
        """ test that the synchronous UDP server closes correctly """
        with patch.object(socket.socket, 'bind') as mock_socket:
            identity = ModbusDeviceIdentification(info={0x00: 'VendorName'})
            server = ModbusUdpServer(context=None, identity=identity)
            server.threads.append(Mock(**{'running': True}))
            server.server_close()
            self.assertEqual(server.control.Identity.VendorName, 'VendorName')
            self.assertFalse(server.threads[0].running)

    def test_udp_server_process(self):
        """ test that the synchronous UDP server processes requests """
        with patch('SocketServer.ThreadingUDPServer') as mock_server:
            server = ModbusUdpServer(None)
            request = ('data', 'socket')
            server.process_request(request, 'client')
            self.assertTrue(mock_server.process_request.called)

    #-----------------------------------------------------------------------#
    # Test Serial Server
    #-----------------------------------------------------------------------#
    def test_serial_server_connect(self):
        with patch.object(serial, 'Serial') as mock_serial:
            mock_serial.return_value = "socket"
            identity = ModbusDeviceIdentification(info={0x00: 'VendorName'})
            server = ModbusSerialServer(context=None, identity=identity)
            self.assertEqual(server.socket, "socket")
            self.assertEqual(server.control.Identity.VendorName, 'VendorName')

            server._connect()
            self.assertEqual(server.socket, "socket")

        with patch.object(serial, 'Serial') as mock_serial:
            mock_serial.side_effect = serial.SerialException()
            server = ModbusSerialServer(None)
            self.assertEqual(server.socket, None)

    def test_serial_server_serve_forever(self):
        """ test that the synchronous serial server closes correctly """
        with patch.object(serial, 'Serial') as mock_serial:
            with patch('pymodbus3.server.sync.ModbusSingleRequestHandler') as mock_handler:
                server = ModbusSerialServer(None)
                instance = mock_handler.return_value
                instance.handle.side_effect = server.server_close
                server.serve_forever()
                instance.handle.assert_any_call()

    def test_serial_server_close(self):
        """ test that the synchronous serial server closes correctly """
        with patch.object(serial, 'Serial') as mock_serial:
            instance = mock_serial.return_value
            server = ModbusSerialServer(None)
            server.server_close()
            instance.close.assert_any_call()

    #-----------------------------------------------------------------------#
    # Test Synchronous Factories
    #-----------------------------------------------------------------------#
    def test_start_tcp_server(self):
        """ Test the tcp server starting factory """
        with patch.object(ModbusTcpServer, 'serve_forever') as mock_server:
            with patch.object(SocketServer.TCPServer, 'server_bind') as mock_binder:
                StartTcpServer()

    def test_start_udp_server(self):
        """ Test the udp server starting factory """
        with patch.object(ModbusUdpServer, 'serve_forever') as mock_server:
            with patch.object(SocketServer.UDPServer, 'server_bind') as mock_binder:
                StartUdpServer()

    def test_start_serial_server(self):
        """ Test the serial server starting factory """
        with patch.object(ModbusSerialServer, 'serve_forever') as mock_server:
            StartSerialServer()

#---------------------------------------------------------------------------#
# Main
#---------------------------------------------------------------------------#
if __name__ == "__main__":
    unittest.main()
