package com.example.myproject;

import org.yamcs.algorithms.AlgorithmException;
import org.yamcs.algorithms.AlgorithmExecutionContext;
import org.yamcs.algorithms.AlgorithmExecutionResult;
import org.yamcs.algorithms.AlgorithmExecutor;
import org.yamcs.logging.Log;
import org.yamcs.parameter.ParameterValue;
import org.yamcs.parameter.UInt32Value;
import org.yamcs.parameter.Value;
import org.yamcs.xtce.Algorithm;
import org.yamcs.xtce.CustomAlgorithm;
import org.yamcs.xtce.Parameter;
import org.yamcs.xtceproc.ProcessingData;

public class OneResultAlgorithm implements AlgorithmExecutor {
    
    private Log log;
    private CustomAlgorithm alg;
    private AlgorithmExecutionContext ctxt;
    private Parameter inputParam;
    private Parameter outputParam;
    private int lastInputValue;

    public OneResultAlgorithm(CustomAlgorithm alg,
            AlgorithmExecutionContext ctxt) {

        this.alg = alg;
        this.ctxt = ctxt;
        inputParam = alg.getInputList().get(0).getParameterInstance().getParameter();
        outputParam = alg.getOutputList().get(0).getParameter();
        log = new Log(getClass());
        log.info("Initialized algorithm {} input={} output={}", getClass().getSimpleName(),
                inputParam.getQualifiedName(), outputParam.getQualifiedName());
    }
    
    @Override
    public Algorithm getAlgorithm() {
        return alg;
    }

    @Override
    public AlgorithmExecutionContext getExecutionContext() {
        return ctxt;
    }

    @Override
    public boolean update(ProcessingData processingData) {
        for (ParameterValue pv : processingData.getTmParams()) {
            if (pv.getParameter().getQualifiedName().equals(inputParam.getQualifiedName())) {
                log.info("Input parameter {} is updated - need to run algorithm", inputParam.getQualifiedName());
                lastInputValue = pv.getEngValue().getUint32Value();
                return true;
            }
        }

        return false;
    }

    @Override
    public AlgorithmExecutionResult execute(long acqTime, long genTime, ProcessingData data)
            throws AlgorithmException {

        ParameterValue value = new ParameterValue(outputParam);
        value.setAcquisitionTime(acqTime);
        value.setGenerationTime(genTime);
        Value v = new UInt32Value(2 * lastInputValue);
        value.setRawValue(v);
        value.setEngValue(v);
        log.info("Returning one algorithm result: {}", value);
        return new AlgorithmExecutionResult(value);
    }

}
