import os
import sys
import threading
import unittest
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from urllib.parse import urlencode
from unittest.mock import patch

sys.path.insert(
    0, os.path.join(os.path.dirname(_file_), "Server")
)

import virtuallab_server as vs


class TestServidorVirtualLab(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.servidor = vs.Server(
            ("127.0.0.1", 0), vs.RequestHandler
        )
        cls.hilo = threading.Thread(
            target=cls.servidor.serve_forever,
            daemon=True
        )
        cls.hilo.start()

        puerto = cls.servidor.server_address[1]
        cls.url = f"http://127.0.0.1:{puerto}"

    @classmethod
    def tearDownClass(cls):
        cls.servidor.shutdown()
        cls.servidor.server_close()
        cls.hilo.join(timeout=2)

    def solicitar(self, ruta, metodo="GET", datos=None):
        cuerpo = None
        headers = {}

        if datos is not None:
            cuerpo = urlencode(datos).encode("utf-8")
            headers["Content-Type"] = (
                "application/x-www-form-urlencoded"
            )

        solicitud = Request(
            self.url + ruta,
            data=cuerpo,
            headers=headers,
            method=metodo
        )

        try:
            with urlopen(solicitud, timeout=3) as respuesta:
                return (
                    respuesta.status,
                    respuesta.read().decode("utf-8")
                )
        except HTTPError as error:
            return (
                error.code,
                error.read().decode("utf-8")
            )

    def test_registrar_usuario(self):
        with patch.object(
            vs.virtuallab_functions,
            "registerUser",
            return_value="Usuario registrado"
        ) as funcion:
            codigo, texto = self.solicitar(
                "/register", "POST",
                {
                    "name": "Ana",
                    "id": "100",
                    "role": "student",
                    "password": "clave123"
                }
            )

        self.assertEqual(codigo, 200)
        self.assertEqual(texto, "Usuario registrado")
        funcion.assert_called_once_with(
            "Ana", "100", "student", "clave123"
        )

    def test_inicio_sesion(self):
        with patch.object(
            vs.virtuallab_functions,
            "openSession",
            return_value="Session was succesfully opened"
        ):
            codigo, texto = self.solicitar(
                "/login", "POST",
                {"id": "100", "password": "clave123"}
            )

        self.assertEqual(codigo, 200)
        self.assertEqual(
            texto, "Session was succesfully opened"
        )

    def test_cerrar_sesion(self):
        with patch.object(
            vs.virtuallab_functions,
            "closeSession",
            return_value="Session was succesfully closed"
        ):
            codigo, texto = self.solicitar(
                "/logout", "POST", {"id": "100"}
            )

        self.assertEqual(codigo, 200)
        self.assertEqual(
            texto, "Session was succesfully closed"
        )

    def test_listar_laboratorios_estudiante(self):
        with patch.object(
            vs.virtuallab_functions,
            "listStudentLabs",
            return_value='["lab1.zip"]'
        ) as funcion:
            codigo, texto = self.solicitar(
                "/list_student_labs",
                metodo="GET",
                datos={"id": "200"}
            )

        self.assertEqual(codigo, 200)
        self.assertEqual(texto, '["lab1.zip"]')
        funcion.assert_called_once_with("200")
   
if _name_ == "_main_":
    unittest.main(verbosity=2)