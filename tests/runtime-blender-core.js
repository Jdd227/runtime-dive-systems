/* RunTime Dive Systems — Trimix Fill Station, independent ideal-gas calculation engine.
 * v0.2.0 | Experimental validation build, not certified for live gas fills.
 * All calculations use unrounded inputs and results. Presentation rounding is separate.
 * Copyright (c) 2026 RunTime Dive Systems. Prototype for owner evaluation.
 */
(function(root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.RunTimeBlend = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function() {
  'use strict';
  const BAR_PER_PSI = 1 / 14.503773800722;
  const PSI_PER_BAR = 14.503773800722;
  const ATM_BAR = 1.01325;
  const TOL = 1e-7;
  const SOURCE_NAMES = ['Helium','Oxygen','Top-off'];
  function finite(n, field) { if (typeof n !== 'number' || !Number.isFinite(n)) throw new Error(field + ' must be a finite number.'); return n; }
  function range(n, field, lo, hi) { finite(n, field); if (n < lo || n > hi) throw new Error(field + ' must be between ' + lo + ' and ' + hi + '.'); return n; }
  function pressureToBar(n, units) { finite(n,'Pressure'); return units === 'psi' ? n * BAR_PER_PSI : n; }
  function barToPressure(n, units) { return units === 'psi' ? n * PSI_PER_BAR : n; }
  function fractions(oxygen, helium, label) {
    range(oxygen, label + ' oxygen', 0, 100); range(helium, label + ' helium', 0, 100);
    if (oxygen + helium > 100 + TOL) throw new Error(label + ' oxygen and helium exceed 100%.');
    return { o: oxygen / 100, h: helium / 100, n: Math.max(0, 1 - (oxygen + helium) / 100) };
  }
  function solve3(matrix, rhs) {
    const a = matrix.map((r, i) => [...r, rhs[i]]);
    for (let c = 0; c < 3; c++) {
      let pivot = c;
      for (let r = c + 1; r < 3; r++) if (Math.abs(a[r][c]) > Math.abs(a[pivot][c])) pivot = r;
      if (Math.abs(a[pivot][c]) < 1e-11) throw new Error('The selected gas sources are not independent. Change the top-off gas or source purity.');
      [a[c], a[pivot]] = [a[pivot], a[c]];
      const factor = a[c][c]; for (let j = c; j < 4; j++) a[c][j] /= factor;
      for (let r = 0; r < 3; r++) if (r !== c) { const mult = a[r][c]; for (let j = c; j < 4; j++) a[r][j] -= mult * a[c][j]; }
    }
    return [a[0][3], a[1][3], a[2][3]];
  }
  function makeSources(args) {
    const hePurity = args.hePurity == null ? 100 : args.hePurity;
    const o2Purity = args.o2Purity == null ? 100 : args.o2Purity;
    range(hePurity, 'Helium source purity', 50, 100);
    range(o2Purity, 'Oxygen source purity', 50, 100);
    const top = fractions(args.topO2 == null ? 20.95 : args.topO2, args.topHe == null ? 0 : args.topHe, 'Top-off gas');
    const he = { o: 0, h: hePurity / 100, n: 1 - hePurity / 100 };
    const ox = { o: o2Purity / 100, h: 0, n: 1 - o2Purity / 100 };
    return [he, ox, top];
  }
  function clampZero(n) { return Math.abs(n) < TOL ? 0 : n; }
  function blend(args) {
    const units = args.units === 'bar' ? 'bar' : 'psi';
    const start = fractions(args.startO2, args.startHe, 'Starting mix');
    const target = fractions(args.targetO2, args.targetHe, 'Target mix');
    const startBar = pressureToBar(args.startPressure, units);
    const finalBar = pressureToBar(args.finalPressure, units);
    range(startBar, 'Starting pressure (bar)', 0, 700); range(finalBar, 'Target pressure (bar)', 0.01, 700);
    if (startBar > finalBar + TOL) throw new Error('Starting pressure exceeds target pressure. A top-up cannot reduce pressure.');
    const basis = args.basis === 'absolute' ? 'absolute' : 'gauge';
    const ambientBar = args.ambientBar == null ? ATM_BAR : range(args.ambientBar, 'Ambient pressure (bar)', 0.7, 1.2);
    const offset = basis === 'absolute' ? ambientBar : 0;
    const sources = makeSources(args);
    const m = [sources.map(s => s.o), sources.map(s => s.h), sources.map(s => s.n)];
    const rightAt = p => {
      const P0 = p + offset, P1 = finalBar + offset;
      return [P1 * target.o - P0 * start.o, P1 * target.h - P0 * start.h, P1 * target.n - P0 * start.n];
    };
    const calculationAt = p => solve3(m, rightAt(p));
    const sourceAtExisting = calculationAt(startBar);
    let usedStart = startBar, bledDown = false;
    let impossibility = null;
    const feasible = additions => additions.every(x => x >= -TOL);
    if (!feasible(sourceAtExisting)) {
      if (args.autoBleed === false) {
        return { ok: false, kind: 'bleed_required', reason: 'Current gas cannot be converted to this target without reducing starting pressure.', startBar, finalBar, sourceAtExisting: sourceAtExisting.map(x => barToPressure(x,units)) };
      }
      // Each source addition varies linearly with the retained starting-gas pressure.
      // Intersect all three half-spaces to find maximum feasible retained pressure.
      const atZero = calculationAt(0), atOne = calculationAt(1);
      let low = 0, high = Math.min(startBar, finalBar);
      for (let i = 0; i < 3; i++) {
        const intercept = atZero[i], slope = atOne[i] - atZero[i];
        if (Math.abs(slope) < 1e-10) { if (intercept < -TOL) impossibility = 'Selected sources cannot create the target mix, even from nominal zero gauge.'; }
        else if (slope < 0) high = Math.min(high, -intercept / slope);
        else low = Math.max(low, -intercept / slope);
      }
      if (impossibility || high < low - TOL || high < -TOL) {
        return { ok: false, kind: 'impossible', reason: impossibility || 'Selected source gases cannot produce the target composition, even after bleed-down.' };
      }
      usedStart = Math.max(0, Math.min(startBar, high));
      bledDown = startBar - usedStart > TOL;
    }
    let addsBar = calculationAt(usedStart).map(clampZero);
    if (!feasible(addsBar)) return {ok:false, kind:'impossible', reason:'Numerical validation failed: one or more source contributions would be negative.'};
    addsBar = addsBar.map(x => Math.max(0,x));
    let pressure = usedStart, stage = [];
    const componentAmounts = {o:(usedStart+offset)*start.o, h:(usedStart+offset)*start.h, n:(usedStart+offset)*start.n};
    for (let i = 0; i < 3; i++) {
      pressure += addsBar[i];
      for (const component of ['o','h','n']) componentAmounts[component] += addsBar[i] * sources[i][component];
      const actualAbsEq = pressure + offset;
      const stageMix = {o:100*componentAmounts.o/actualAbsEq,h:100*componentAmounts.h/actualAbsEq,n:100*componentAmounts.n/actualAbsEq};
      stage.push({ mix: stageMix, name: SOURCE_NAMES[i], source: sources[i], addedBar: addsBar[i], stopBar: pressure,
        added: barToPressure(addsBar[i],units), stop: barToPressure(pressure,units) });
    }
    const P0 = usedStart + offset, P1 = finalBar + offset;
    const component = key => (P0 * start[key] + addsBar.reduce((sum, x, i) => sum + x * sources[i][key],0)) / P1 * 100;
    const produced = { o: component('o'), h: component('h'), n: component('n') };
    const closureBar = pressure - finalBar;
    const closurePercent = Math.max(Math.abs(produced.o - args.targetO2), Math.abs(produced.h - args.targetHe), Math.abs(produced.n - (100 - args.targetO2 - args.targetHe)));
    if (Math.abs(closureBar) > 1e-6 || closurePercent > 1e-6) throw new Error('Internal mass-balance audit failed. Do not use these results.');
    return {
      ok:true, units, basis, ambientBar, initialBar:startBar, retainedBar:usedStart,
      finalBar, bledDown,
      bleedAmount:barToPressure(startBar-usedStart,units),
      retainedPressure:barToPressure(usedStart,units),
      start, target, sources, stages:stage, produced, closureBar, closurePercent,
      gasLaw:'Ideal gas; equal temperature; known homogeneous gas; cylinder pressure reference '+basis
    };
  }
  function topOff(args) {
    const units = args.units === 'bar' ? 'bar' : 'psi';
    const start = fractions(args.startO2,args.startHe,'Starting mix');
    const top = fractions(args.topO2,args.topHe,'Top-off gas');
    const p0 = pressureToBar(args.startPressure,units);
    const p1 = pressureToBar(args.finalPressure,units);
    const basis = args.basis === 'absolute' ? 'absolute' : 'gauge';
    const offset = basis === 'absolute' ? (args.ambientBar == null ? ATM_BAR : range(args.ambientBar,'Ambient bar',0.7,1.2)) : 0;
    range(p0,'Starting pressure (bar)',0,700); range(p1,'Target pressure (bar)',0.01,700);
    if (p1 < p0) throw new Error('Target pressure must not be below starting pressure.');
    const P0=p0+offset, P1=p1+offset, added=p1-p0;
    const calc = key => 100*(P0*start[key]+added*top[key])/P1;
    return {ok:true, units, added:barToPressure(added,units), finalPressure:barToPressure(p1,units),
      result:{o:calc('o'),h:calc('h'),n:calc('n')}, basis};
  }
  function metrics(args) {
    const mix = fractions(args.o2,args.he,'Analysis mix');
    const depth = range(args.depth,'Depth',0,500);
    const depthUnits = args.depthUnits === 'm' ? 'm' : 'ft';
    const densityAt0 = {o:1.429,n:1.251,h:0.179}; // 0°C, one atmosphere; approximate ideal density.
    const ata = 1 + depth/(depthUnits === 'ft' ? 33 : 10);
    const po2 = mix.o * ata;
    const modPO2 = range(args.modPO2 == null ? 1.4 : args.modPO2,'MOD PPO2',0.1,2);
    const mod = mix.o > 0 ? Math.max(0, (modPO2/mix.o -1) * (depthUnits==='ft'?33:10)) : null;
    const ccr = args.mode === 'ccr';
    let working=mix;
    if (ccr) {
      const setpoint = range(args.setpoint == null ? 1.3 : args.setpoint,'Loop PPO2',0.1,2);
      const loopO = Math.min(1,setpoint/ata);
      const inertTotal=mix.h+mix.n;
      if (inertTotal <= 1e-10) throw new Error('CCR loop composition cannot be inferred from a pure oxygen diluent.');
      working={o:loopO,h:(1-loopO)*(mix.h/inertTotal),n:(1-loopO)*(mix.n/inertTotal)};
    }
    const rho=ata*(working.o*densityAt0.o+working.h*densityAt0.h+working.n*densityAt0.n);
    const depthPerAta=depthUnits === 'ft'?33:10;
    const narcoticBoth=Math.max(0,(ata*(working.o+working.n)-1)*depthPerAta);
    const narcoticN2=Math.max(0, (ata*working.n/0.79-1)*depthPerAta);
    return {ata, po2, mod, rho, endBoth:narcoticBoth,endN2:narcoticN2, working,
      densityStatus:rho>6.3?'high':rho>5.2?'caution':'preferred', mode:ccr?'ccr':'oc', depthUnits};
  }
  function temperature(args) {
    const units = args.units === 'bar'?'bar':'psi';
    const p=pressureToBar(args.pressure, units);
    const ambient=args.ambientBar==null?ATM_BAR:range(args.ambientBar,'Ambient pressure (bar)',0.7,1.2);
    range(p,'Observed pressure (bar)',0,700);
    const fToK = f => (f - 32)*5/9 + 273.15;
    const from = args.tempUnits === 'C'?args.fromTemp+273.15:fToK(args.fromTemp);
    const to = args.tempUnits === 'C'?args.toTemp+273.15:fToK(args.toTemp);
    range(from,'Measured temperature K',180,400); range(to,'Target temperature K',180,400);
    const corrected=(p+ambient)*to/from-ambient;
    if (corrected<0) throw new Error('Predicted settled pressure is below zero gauge.');
    return { settledPressure:barToPressure(corrected,units), delta:barToPressure(corrected-p,units), units};
  }
  return {blend,topOff,metrics,temperature,pressureToBar,barToPressure,fractions,PSI_PER_BAR,BAR_PER_PSI,ATM_BAR};
});
