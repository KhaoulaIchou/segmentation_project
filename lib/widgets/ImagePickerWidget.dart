import 'dart:io';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';

class MyHomePage extends StatefulWidget {
  MyHomePage({Key? key, required this.title}) : super(key: key);

  final String title;

  @override
  _MyHomePageState createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  final _controller = TextEditingController();
  late File _image;

  Future<void> _chooseImage() async {
    final pickedImage =
    await ImagePicker().pickImage(source: ImageSource.gallery);
    setState(() {
      _image = File(pickedImage!.path);
    });
  }

  Future<void> _processImage() async {
    final url = 'http://192.168.1.33:8000/process-image';
    final request = http.MultipartRequest('POST', Uri.parse(url));
    request.files.add(await http.MultipartFile.fromPath('image', _image.path));
    final response = await request.send();

    if (response.statusCode == 200) {
      final bytes = await response.stream.toBytes();
      final image = Image.memory(bytes);
      showDialog(
        context: context,
        builder: (_) => AlertDialog(
          content: SingleChildScrollView(
            child: Column(
              children: [
                Text('Processed Image'),
                SizedBox(height: 20),
                Container(
                  height: 300,
                  child: FittedBox(
                    child: image,
                    fit: BoxFit.fill,
                  ),
                ),
              ],
            ),
          ),
        ),
      );
    } else {
      showDialog(
        context: context,
        builder: (_) => AlertDialog(
          content: Text('Error processing image: ${response.reasonPhrase}'),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            TextField(
              controller: _controller,
              decoration: InputDecoration(
                border: OutlineInputBorder(),
                labelText: 'Message',
              ),
            ),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: _chooseImage,
              child: Text('Choose Image'),
            ),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: _processImage,
              child: Text('Process Image'),
            ),
          ],
        ),
      ),
    );
  }
}
