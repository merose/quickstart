package com.example.myproject;

import java.nio.ByteBuffer;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.atomic.AtomicInteger;

import org.yamcs.TmPacket;
import org.yamcs.YConfiguration;
import org.yamcs.tctm.AbstractPacketPreprocessor;
import org.yamcs.utils.TimeEncoding;

/**
 * Component capable of modifying packet binary received from a link, before passing it further into Yamcs.
 * <p>
 * A single instance of this class is created, scoped to the link udp-in.
 * <p>
 * This is specified in the configuration file yamcs.myproject.yaml:
 * 
 * <pre>
 * ...
 * dataLinks:
 *   - name: udp-in
 *     class: org.yamcs.tctm.UdpTmDataLink
 *     stream: tm_realtime
 *     host: localhost
 *     port: 10015
 *     packetPreprocessorClassName: com.example.myproject.MyPacketPreprocessor
 * ...
 * </pre>
 */
public class MyPacketPreprocessor extends AbstractPacketPreprocessor {
	
	enum Epoch {
		
		TAI, UNIX, GPS, J2000;
		
		public long timeFromMillis(long millis) {
			switch (this) {
			case TAI:
				return TimeEncoding.fromTaiMillisec(millis);
			case UNIX:
				return TimeEncoding.fromUnixMillisec(millis);
			case J2000:
				return TimeEncoding.fromJ2000Millisec(millis);
			case GPS:
				return TimeEncoding.fromGpsMillisec(millis);
			default:
				throw new IllegalStateException("Should not happen: Illegal value for time epoch: " + this);	
			}
		}
	}
	
	
	public static final String TIME_OFFSET_KEY = "timeOffset";
	public static final String TIME_LENGTH_KEY = "timeLength";
	public static final String FRACTION_LENGTH_KEY = "fractionLength";
	public static final String TIME_EPOCH_KEY = "timeEpoch";

	private int timeOffset;
	private int timeLength;
	private double timeScale;
	Epoch timeEpoch;

    private Map<Integer, AtomicInteger> seqCounts = new HashMap<>();

    // Constructor used when this preprocessor is used without YAML configuration
    public MyPacketPreprocessor(String yamcsInstance) {
        this(yamcsInstance, YConfiguration.emptyConfig());
    }

    // Constructor used when this preprocessor is used with YAML configuration
    // (packetPreprocessorClassArgs)
    public MyPacketPreprocessor(String yamcsInstance, YConfiguration config) {
        super(yamcsInstance, config);
        
        // Default to a 4+2 time, in seconds+fraction.
        timeOffset = config.getInt(TIME_OFFSET_KEY, -1);
        timeLength = config.getInt(TIME_LENGTH_KEY, 6);
        int fractionLength = config.getInt(FRACTION_LENGTH_KEY, 2);
        timeScale = 1.0;
        for (int i=0; i < fractionLength; ++i) {
        	timeScale /= 256.0;
        }
        String epochName = config.getString(TIME_EPOCH_KEY, Epoch.UNIX.name());
        
        if (timeLength > 8) {
        	eventProducer.sendWarning("CONFIG",
        			String.format("Time length in secondary header must be <= 8, timeLength: %d",
        					timeLength));
        	timeLength = -1;
        }
        try {
        	timeEpoch = Epoch.valueOf(epochName.toUpperCase());
        } catch (IllegalArgumentException ex) {
        	eventProducer.sendWarning("CONFIG", "Time epoch is invalid: " + epochName);
        	timeEpoch = Epoch.UNIX;
        }
    }

    @Override
    public TmPacket process(TmPacket packet) {

        byte[] bytes = packet.getPacket();
        if (bytes.length < 6) { // Expect at least the length of CCSDS primary header
            eventProducer.sendWarning("SHORT_PACKET",
                    String.format("Short packet received, length: %d; minimum required length is 6 bytes", + bytes.length));

            // If we return null, the packet is dropped.
            return null;
        }

        // Verify continuity for a given APID based on the CCSDS sequence counter
        int apidseqcount = ByteBuffer.wrap(bytes).getInt(0);
        int apid = (apidseqcount >> 16) & 0x07FF;
        int seq = (apidseqcount) & 0x3FFF;
        AtomicInteger ai = seqCounts.computeIfAbsent(apid, k -> new AtomicInteger());
        int oldseq = ai.getAndSet(seq);

        if (((seq - oldseq) & 0x3FFF) != 1) {
            eventProducer.sendWarning("SEQ_COUNT_JUMP",
                    "Sequence count jump for APID: " + apid + " old seq: " + oldseq + " newseq: " + seq);
        }

        if (timeOffset < 0 || (apidseqcount & 0x08000000) == 0) {
        	// No time in the secondary header. Use the Yamcs time.
            packet.setGenerationTime(TimeEncoding.getWallclockTime());
        } else if (bytes.length < timeOffset + timeLength) {
        	eventProducer.sendWarning("SHORT_PACKET",
        			String.format("Packet has secondary header but is too short for time field, length: %d",
        					bytes.length));
            packet.setGenerationTime(TimeEncoding.getWallclockTime());
        } else {
        	long timeRaw = 0;
        	for (int i=0; i < timeLength; ++i) {
        		timeRaw = (timeRaw << 8) | (bytes[timeOffset+i] & 0xFF);
        	}
        	
        	long millis = Math.round(timeRaw * timeScale * 1000);
        	packet.setGenerationTime(timeEpoch.timeFromMillis(millis));
        }

        // Use the full 32-bits, so that both APID and the count are included.
        // Yamcs uses this attribute to uniquely identify the packet (together with the gentime)
        packet.setSequenceCount(apidseqcount);

        return packet;
    }
}
