# =============================================================================
#                           UFCD 10794 - Projecto 2 - Segunda Fase
# =============================================================================

__aplicacao__ = 'PandaEncoder'
__criadores__ = ['Goncalo Cabral, Maria Sampaio, Alexandre Melim']
__github__ = 'https://github.com/alexdyaz/PandaEncoder'
__curso__ = ['UFCD 10794 - Projecto 2 - Segunda Fase']
__data__ = '2022/02/22'
__status__ = 'Em desenvolvimento'
__descricao__ = 'LZSS Encoder/ Decoder'

# =============================================================================
#
# =============================================================================

from encodings import utf_8
import os
import subprocess
import io
import math
import bitstruct
import pathlib
from typing import Union, BinaryIO, Tuple, Iterable
from bitarray import bitarray
from collections import deque
from docopt import docopt

print('Aplicacao: ' + __aplicacao__)
print('Criadores: ' + ', '.join(__criadores__))
print('Pagina Github do Projecto: ' + __github__)
print('Curso: ' + ', '.join(__curso__))
print('Data: ' + __data__)
print('Estado: ' + __status__)
print('Descricao: ' + __descricao__)

usage = '''

usage:
	pzyp.py -d  <file_name>
	pzyp.py -c -s <file_name>      
	pzyp.py -c -m <file_name> 
	pzyp.py -c -l <file_name>    
	pzyp.py -c -xl <file_name> 
'''

UNENCODED_STRING_SIZE = 8  # in bits
# ENCODED_OFFSET_SIZE = 24
ENCODED_OFFSET_SIZE = 12  # in bits
ENCODED_LEN_SIZE = 4  # in bits
ENCODED_STRING_SIZE = ENCODED_OFFSET_SIZE + ENCODED_LEN_SIZE  # in bits

WINDOW_SIZE = 2 ** ENCODED_OFFSET_SIZE  # in bytes
BREAK_EVEN_POINT = ENCODED_STRING_SIZE // 8  # in bytes
MIN_STRING_SIZE = BREAK_EVEN_POINT + 1  # in bytes
MAX_STRING_SIZE = 2 ** ENCODED_LEN_SIZE - 1 + MIN_STRING_SIZE  # in bytes


class PZYPContext:

	def __init__(
			self,
			encoded_offset_size=ENCODED_OFFSET_SIZE,
			encoded_len_size=ENCODED_LEN_SIZE,
			unenc_string_size=UNENCODED_STRING_SIZE,
	):
		self._encoded_offset_size = encoded_offset_size
		self._encoded_len_size = encoded_len_size
		self._unencoded_string_size = unenc_string_size

	@property
	def encoded_offset_size(self):
		return self._encoded_offset_size

	@property
	def encoded_len_size(self):
		return self._encoded_len_size

	@property
	def unencoded_string_size(self):
		return self._unencoded_string_size

	@property
	def encoded_string_size(self) -> int:
		return self.encoded_offset_size + self.encoded_len_size  # in bits

	@property
	def window_size(self) -> int:
		return 2 ** self.encoded_offset_size  # in bytes

	@property
	def break_even_point(self) -> int:
		return self.encoded_string_size // 8  # in bytes

	@property
	def min_string_size(self) -> int:
		return self.break_even_point + 1  # in bytes

	@property
	def max_string_size(self) -> int:
		return 2 ** self.encoded_len_size - 1 + self.min_string_size  # in bytes


class LZSSWriter:

	def __init__(
			self,
			out: BinaryIO,
			ctx=PZYPContext(),
			close_out_stream=False,
	):
		self.buffer = bitarray()
		self._close_out_stream = close_out_stream
		self._out = out
		self._ctx = ctx
		self._enc_fmt = bitstruct.compile(
			f'u{ctx.encoded_offset_size}u{ctx.encoded_len_size}'
		)
		self._inner_bitify_enc = self._bitify_enc_not_multiple_of_8
		if (ctx.encoded_offset_size + ctx.encoded_len_size) % 8 == 0:
			self._inner_bitify_enc = self._bitify_enc_multiple_of_8

	def write(self, data: Union[bytes, Tuple[int, int]]):
		(self._bitify_unenc if isinstance(data, bytes) else self._bitify_enc)(data)
		if len(self.buffer) == 32_768:
			self._stream_bits()

	def _bitify_enc(self, enc_data: Tuple[int, int]) -> int:
		pos, len_ = enc_data
		ctx = self._ctx
		assert pos < ctx.window_size, f'pos={pos}'
		assert ctx.min_string_size <= len_ <= ctx.max_string_size, f'pos = {pos}, len = {len_}'
		mapped_len = len_ - ctx.min_string_size
		self.buffer.append(True)
		self._inner_bitify_enc(pos, mapped_len)
		return ctx.encoded_string_size  # remember: it's in bits ...

	def _bitify_enc_not_multiple_of_8(self, pos: int, mapped_len: int):
		enc_fmt = self._enc_fmt
		bitarr = bitarray()
		bitarr.frombytes(enc_fmt.pack(pos, mapped_len))
		self.buffer.extend(bitarr[:enc_fmt.calcsize()])

	def _bitify_enc_multiple_of_8(self, pos: int, mapped_len: int):
		self.buffer.frombytes(self._enc_fmt.pack(pos, mapped_len))

	def _bitify_unenc(self, unenc_data: bytes) -> int:
		assert unenc_data
		self.buffer.append(False)
		self.buffer.frombytes(unenc_data)
		return self._ctx.unencoded_string_size

	def _stream_bits(self, size_in_bits: int = 2 ** 63 - 1):
		data = self.buffer[:size_in_bits].tobytes()
		del self.buffer[:size_in_bits]
		self._out.write(data)

	def close(self, flush_buffer=True):
		if flush_buffer:
			self._flush_buffer()
		if self._close_out_stream:
			self._out.close()

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		# Flush the buffer only if an exception hasn't occurred
		self.close(not exc_value)

	def _flush_buffer(self):
		if self.buffer:
			self.buffer.fill()  # pad buffer with 0s to get
			self._stream_bits()  # an integral number of bytes


class LZSSReader:

	def __init__(
			self,
			in_: BinaryIO,
			ctx=PZYPContext(),
			close_in_stream=False,
	):
		self.buffer = bitarray()
		self.close_in_stream = close_in_stream
		self._in = in_
		self._ctx = ctx
		self._enc_fmt = bitstruct.compile(
			f'u{ctx.encoded_offset_size}u{ctx.encoded_len_size}'
		)

	def read(self):
		ctx = self._ctx
		assert len(self.buffer) <= ctx.encoded_string_size + 8

		if self._end_of_data():
			return False, b''

		if not self.buffer:
			self.buffer.frombytes(self._in.read(1))
		encoded = bool(self.buffer[0])

		needed_bits = 1 + [ctx.unencoded_string_size, ctx.encoded_string_size][encoded]
		bytes_to_read = math.ceil((needed_bits - len(self.buffer)) / 8)
		self.buffer.frombytes(self._in.read(bytes_to_read))

		data: bitarray = self.buffer[1:needed_bits]
		del self.buffer[:needed_bits]

		if encoded:
			pos, len_ = self._enc_fmt.unpack(data.tobytes())
			return True, (pos, len_ + ctx.min_string_size)
		return False, data.tobytes()

	def _end_of_data(self) -> bool:

		buffer_maybe_empty = (
				not self.buffer or
				(self.buffer.count(0) == len(self.buffer) and len(self.buffer) < 8)
		)
		curr_pos = self._in.tell()
		eof = buffer_maybe_empty and not self._in.read(1)
		self._in.seek(curr_pos)
		return eof

	def __iter__(self):
		return self

	def __next__(self):
		data = self.read()
		if not data[1]:
			raise StopIteration()
		return data

	def close(self):
		assert len(self.buffer) < 16
		empty_buffer = not self.buffer or self.buffer.count(0) == len(self.buffer)
		if not empty_buffer:
			raise LZSSReader.UnreadData(
				'Unread compressed data in buffer.'
			)
		if self.close_in_stream:
			self._in.close()

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		self.close()

	class UnreadData(Exception):
		pass


def textChar_elements(textChar_verify2, buffer2):
	textChar_count = 0
	distance = 0

	for element in buffer2:

		if len(textChar_verify2) <= distance:
			return textChar_count - len(textChar_verify2)

		if textChar_verify2[distance] == element:
			distance += 1
		else:
			distance = 0

		textChar_count += 1

	return -1


def encode(in_: BinaryIO, out: BinaryIO, lzss_writer=None, ctx=PZYPContext()):
	with (lzss_writer or LZSSWriter(out, ctx)) as lzss_out:
		args = docopt(usage)
		if args['-s']:
			window = 1024
			ENCODED_OFFSET_SIZE = 10  # in bits
		elif args['-m']:
			window = 4096
			ENCODED_OFFSET_SIZE = 12  # in bits
		elif args['-l']:
			window = 16384
			ENCODED_OFFSET_SIZE = 14  # in bits
		elif args['-xl']:
			window = 32768
			ENCODED_OFFSET_SIZE = 15  # in bits

		buffer = deque(maxlen=window)
		textChar_verify = []
		output = []
		flagEnd = 0
		flag_done = 0
		i = 0
		flag_go = 0
		text = in_.read()
		for char in text:
			index = textChar_elements(textChar_verify, buffer)
			if textChar_elements(textChar_verify + [char], buffer) == -1 or i == len(text) - 1 or flag_go == 1:

				if i == len(text) - 1 and textChar_elements(textChar_verify + [char], buffer) != -1:
					flagEnd = 1
					textChar_verify.append(char)

				if len(textChar_verify) > 1:
					index = textChar_elements(textChar_verify, buffer)
					distance = i - index - len(textChar_verify)
					length = len(textChar_verify)
					if flagEnd == 1:
						distance += 1
						flagEnd = 0

					if length < 3:
						for byte_int in textChar_verify:
							lzss_out.write(bytes((byte_int,)))
						if i == len(text) - 1:
							lzss_out.write(bytes((char,)))
					else:
						# print(textChar_verify)
						prefix_pos = distance
						prefix_len = length
						# print("pos",prefix_pos, "len",prefix_len)
						lzss_out.write((prefix_pos, prefix_len))
						flag_go = 0

					buffer.extend(textChar_verify)

				else:
					for byte_int in textChar_verify:
						lzss_out.write(bytes((byte_int,)))
					if i == len(text) - 1:
						lzss_out.write(bytes((char,)))
					buffer.extend(textChar_verify)

				textChar_verify = []

			if char == "<":
				textChar_verify.append(char)
				textChar_verify.append(char)

			if char != "<":
				if len(textChar_verify) < ENCODED_OFFSET_SIZE:
					textChar_verify.append(char)

				else:
					flag_go = 1
					textChar_verify.append(char)

			if len(buffer) > window:
				buffer.popleft()

			i += 1

		return 0


def decode(in_: BinaryIO, out: BinaryIO, lzss_reader=None, ctx=PZYPContext()):
	with (lzss_reader or LZSSReader(in_, ctx)) as lzss_in:
		output = []
		var_bytes = b''

		for encoded_flag, elemento in lzss_in:

			if encoded_flag:
				prefix_pos, prefix_len = elemento
				actualText = output[-prefix_pos:][:prefix_len]
				actualText_1 = b''.join(actualText)
				var_bytes += actualText_1
				for part in actualText:
					output.append(part)
			else:
				var_bytes += elemento
				output.append(elemento)

		return var_bytes


def _main():
	ctx = PZYPContext(
		encoded_offset_size=4,  # janela terá 16 bytes
		encoded_len_size=3  # comprimentos de 8 + 1 - 1 = 8 bytes
	)

	args = docopt(usage)
	var_bytes = b''
	if args['-d']:
		ficheiro = input('Insira nome do ficheiro:')
		with open(args['<file_name>'], 'rb') as in_:
			with open(ficheiro, 'wb') as out_1:
				var_bytes += decode(in_, out_1)
				out_1.write(var_bytes)
			print('O ficheiro de saída tem os seguintes dados: ')
			with open(ficheiro, 'rb') as out_2:
				dados_comp = out_2.read()
				print(dados_comp)
				try:
					subprocess.call([os.system(ficheiro)])
				finally:
					return

	elif args['-c']:
		ficheiro = input('Insira nome do ficheiro:')
		with open(args['<file_name>'], 'rb') as _in:
			with open(ficheiro + '.lzs', 'wb') as out:
				encode(_in, out)
			# out.seek(0)
			# var_test = out.read()
			# print(var_test)
			print('O ficheiro de entrada tem os seguintes dados: ')
			with open(ficheiro + '.lzs', 'rb') as out:
				out.seek(0)
				dados_comp = out.read()
			print(dados_comp)
	else:
		print("command not found")


if __name__ == '__main__':
	_main()
