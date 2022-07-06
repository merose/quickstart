package com.example.myproject;

import static org.junit.Assert.assertEquals;

import org.junit.Before;
import org.junit.Test;
import org.yamcs.TmPacket;
import org.yamcs.YConfiguration;
import org.yamcs.tctm.PacketPreprocessor;
import org.yamcs.utils.TimeEncoding;
import org.yaml.snakeyaml.Yaml;

public class MyPacketPreprocessorTest {

	@Before
	public void init() {
		TimeEncoding.setUp();
	}

	@Test
	public void testEmptyConfig() {
		PacketPreprocessor processor = new MyPacketPreprocessor(null);
		TmPacket packet = makePacket(false, 0, 1, new byte[1]);
		long now = TimeEncoding.getWallclockTime();
		processor.process(packet);
		assert packet.getGenerationTime() >= now;
	}

	@Test
	public void testShortTime() {
		String configStr = "timeOffset: 6\n"
				+ "timeLength: 1\n"
				+ "fractionLength: 0\n"
				+ "timeEpoch: UNIX";
		YConfiguration config = YConfiguration.wrap(new Yaml().load(configStr));
		PacketPreprocessor processor = new MyPacketPreprocessor(null, config);

		TmPacket packet = makePacket(true, 0, 1, new byte[] { 0 });
		processor.process(packet);
		assertEquals(TimeEncoding.fromUnixMillisec(0), packet.getGenerationTime());

		packet = makePacket(true, 0, 2, new byte[] { 1 });
		processor.process(packet);
		assertEquals(TimeEncoding.fromUnixMillisec(1000), packet.getGenerationTime());

		packet = makePacket(true, 0, 3, new byte[] { 127 });
		processor.process(packet);
		assertEquals(TimeEncoding.fromUnixMillisec(127000), packet.getGenerationTime());

		packet = makePacket(true, 0, 4, new byte[] { (byte) 0xFF });
		processor.process(packet);
		assertEquals(TimeEncoding.fromUnixMillisec(255000), packet.getGenerationTime());
	}

	@Test
	public void testLadeeTime() {
		String configStr = "timeOffset: 6\n"
				+ "timeLength: 6\n"
				+ "fractionLength: 2\n"
				+ "timeEpoch: J2000";
		YConfiguration config = YConfiguration.wrap(new Yaml().load(configStr));
		PacketPreprocessor processor = new MyPacketPreprocessor(null, config);

		TmPacket packet = makePacket(true, 0, 1, new byte[] { 0, 0, 0, 0, 0, 0 });
		processor.process(packet);
		assertEquals(TimeEncoding.fromJ2000Millisec(0), packet.getGenerationTime());

		// 1ms is 65.536 fractional units.
		packet = makePacket(true, 0, 2, new byte[] { 0, 0, 0, 0, 0, 66 });
		processor.process(packet);
		assertEquals(TimeEncoding.fromJ2000Millisec(1), packet.getGenerationTime());

		packet = makePacket(true, 0, 3, new byte[] { 0, 0, 0, 1, 0, 0 });
		processor.process(packet);
		assertEquals(TimeEncoding.fromJ2000Millisec(1000), packet.getGenerationTime());

		packet = makePacket(true, 0, 4, new byte[] { 0, 0, 0, 0, (byte) 0xFF, (byte) 0xFF });
		processor.process(packet);
		assertEquals(TimeEncoding.fromJ2000Millisec(1000), packet.getGenerationTime());

		packet = makePacket(true, 0, 5, new byte[] { 0, 0, 1, (byte) 0xFF, 0, 0 });
		processor.process(packet);
		assertEquals(TimeEncoding.fromJ2000Millisec(511000), packet.getGenerationTime());
	}

	@Test
	public void testLongUnixTime() {
		String configStr = "timeOffset: 7\n"
				+ "timeLength: 8\n"
				+ "fractionLength: 4\n"
				+ "timeEpoch: UNIX";
		YConfiguration config = YConfiguration.wrap(new Yaml().load(configStr));
		PacketPreprocessor processor = new MyPacketPreprocessor(null, config);

		// In all these packets, the first 0 is not part of the time, because of the
		// timeOffset of 7, in the configuration above.
		TmPacket packet = makePacket(true, 0, 1, new byte[] { 0, 0, 0, 0, 0, 0, 0, 0, 0 });
		processor.process(packet);
		assertEquals(TimeEncoding.fromUnixMillisec(0), packet.getGenerationTime());

		// 1ms is 4294967.296 fractional units. 4294968==0x418938
		packet = makePacket(true, 0, 2, new byte[] { 0, 0, 0, 0, 0, 0, (byte) 0x41, (byte) 0x89, (byte) 0x38 });
		processor.process(packet);
		assertEquals(TimeEncoding.fromUnixMillisec(1), packet.getGenerationTime());

		packet = makePacket(true, 0, 3, new byte[] { 0, 0, 0, 0, 1, 0, 0, 0, 0 });
		processor.process(packet);
		assertEquals(TimeEncoding.fromUnixMillisec(1000), packet.getGenerationTime());

		packet = makePacket(true, 0, 4, new byte[] { 0, 0, 0, 0, 0, (byte) 0xFF, (byte) 0xFF, (byte) 0xFF, (byte) 0xFF });
		processor.process(packet);
		assertEquals(TimeEncoding.fromUnixMillisec(1000), packet.getGenerationTime());

		packet = makePacket(true, 0, 5, new byte[] { 0, 0, 0, 1, (byte) 0xFF, 0, 0, 0, 0 });
		processor.process(packet);
		assertEquals(TimeEncoding.fromUnixMillisec(511000), packet.getGenerationTime());
	}

	public TmPacket makePacket(boolean hasSecondaryHeader, int apid, int seqCount,
			byte[] userData) {

		if (userData.length == 0) {
			userData = new byte[1];
		}
		byte[] b = new byte[6 + userData.length];
		int apidFlags = apid & 0x7FF;
		if (hasSecondaryHeader) {
			apidFlags |= 0x0800;
		}
		b[0] = (byte) ((apidFlags >> 8) & 0xFF);
		b[1] = (byte) (apidFlags & 0xFF);
		int seqFlags = (seqCount & 0x3FFF) | (0x03 << 14);
		b[2] = (byte) ((seqFlags >> 8) & 0xFF);
		b[3] = (byte) (seqFlags & 0xFF);
		int packetLength = userData.length - 1;
		b[4] = (byte) ((packetLength >> 8) & 0xFF);
		b[5] = (byte) (packetLength & 0xFF);
		System.arraycopy(userData, 0, b, 6, userData.length);

		return new TmPacket(TimeEncoding.getWallclockTime(), b);
	}

}
