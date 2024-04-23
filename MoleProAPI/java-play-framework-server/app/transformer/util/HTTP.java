package transformer.util;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;

import apimodels.ErrorMsg;

public class HTTP {

	public static String get(final URL url) throws IOException {
		return get(url, 0);
	}


	public static String get(final URL url, final int timeout) throws IOException {
		final HttpURLConnection con = (HttpURLConnection)url.openConnection();
		con.setRequestMethod("GET");
		con.setReadTimeout(timeout);
		con.connect();
		return response(url, con);
	}


	public static String post(URL url, String json) throws IOException {
		final HttpURLConnection con = (HttpURLConnection)url.openConnection();
		con.setRequestMethod("POST");
		con.setRequestProperty("Content-Type", "application/json");
		con.setDoOutput(true);
		final OutputStream os = con.getOutputStream();
		os.write(json.getBytes());
		os.close();
		return response(url, con);
	}


	public static String post(final URL url, final String key, final String value) throws IOException {
		final HttpURLConnection con = (HttpURLConnection)url.openConnection();
		con.setRequestMethod("POST");
		con.setDoOutput(true);
		final OutputStream os = con.getOutputStream();
		os.write((key + "=" + value).getBytes());
		os.close();
		return response(url, con);
	}


	private static String response(final URL url, final HttpURLConnection con) throws IOException {
		final int responsecode = con.getResponseCode();
		if (responsecode == 200) {
			return readResponse(con.getInputStream());
		}
		String msg = "Connection failed (" + url + "): " + responsecode;
		try {
			final ErrorMsg errorMsg = JSON.mapper.readValue(readResponse(con.getErrorStream()), ErrorMsg.class);
			msg = msg + " " + errorMsg.getTitle() + ": " + errorMsg.getDetail();
		}
		catch (Exception e) {
			// no extra message on parse error
		}
		throw new IOException(msg);
	}


	private static String readResponse(final InputStream responseStream) throws IOException {
		final BufferedReader input = new BufferedReader(new InputStreamReader(responseStream));
		final StringBuilder response = new StringBuilder();
		for (String line = input.readLine(); line != null; line = input.readLine()) {
			response.append(line).append('\n');
		}
		input.close();
		return response.toString();
	}
}
