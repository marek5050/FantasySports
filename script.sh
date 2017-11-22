#!/Applications/Mathematica.app/Contents/MacOS/MathKernel -script
Print[$CommandLine[[3;;]]]
date = DateString["ISODate"];
fantasyData = 
  Import["/Users/marek5050/machinelearning/NBA/data/predictions/" <> 
    date <> ".csv", "CSV"];
first = First@fantasyData;
fantasyData = Delete[fantasyData, 1];

DKFPS = First@Flatten@Position[first, "DKFPS"];
RandomForest = First@Flatten@Position[first, "Random Forest"];
AdaBoost =  First@Flatten@Position[first, "AdaBoost"];
NeuralNetwork =  First@Flatten@Position[first, "Neural Network"];
Team = First@Flatten@Position[first, "Team"];
Salary = First@Flatten@ Position[first, "Salary"];
Pos = First@Flatten@Position[first, "Position"];
Home = First@Flatten@Position[first, "Home"];
Name = First@Flatten@Position[first, "Name"];

generateRosterCombined[algo_] := 
 Module[{c, salaries, A, pos, team, sg, pg, g, pf, sf, f, s, p, cen, 
   cen1, bos, den, gs, cle, min, mem, dal, m, b, res, lac, okc, ny, 
   hou, mil, pho, por, ind},
  c = -1 * (fantasyData[[All, algo]]);
  salaries = fantasyData[[All, Salary]];
  A = Join[-1*{salaries, 
      ConstantArray[1, Length@salaries]}, {ConstantArray[1, 
      Length@salaries]}];
  pos = fantasyData[[All, Pos]]; 
  team = fantasyData[[All, Team]];
  sg = StringContainsQ[#, "SG"] & /@ pos /. {True -> 1, False -> 0};
  pg = StringContainsQ[#, "PG"] & /@ pos /. {True -> 1, False -> 0}; 
  g = StringContainsQ[#, "G"] & /@ pos /. {True -> 1, False -> 0}; 
  pf = StringContainsQ[#, "PF"] & /@ pos /. {True -> 1, False -> 0}; 
  sf = StringContainsQ[#, "SF"] & /@ pos /. {True -> 1, False -> 0}; 
  f = StringContainsQ[#, "F"] & /@ pos /. {True -> 1, False -> 0}; 
  s = StringContainsQ[#, "S"] & /@ pos /. {True -> 1, False -> 0}; 
  p = StringContainsQ[#, "P"] & /@ pos /. {True -> 1, False -> 0}; 
  cen  = StringContainsQ[#, "C"] & /@ pos /. {True -> 1, False -> 0}; 
  cen1 = StringMatchQ[#, "C"] & /@ pos /. {True -> 1, False -> 0};
  bos = StringContainsQ[#, "BOS"] & /@ team /. {True -> 1, False -> 0};
  den = StringContainsQ[#, "Den"] & /@ team /. {True -> 1, False -> 0};
  min = StringContainsQ[#, "MIN"] & /@ team /. {True -> 1, False -> 0};
  cle = StringContainsQ[#, "CLE"] & /@ team /. {True -> 1, False -> 0};
  mem = StringContainsQ[#, "MEM"] & /@ team /. {True -> 1, False -> 0};
  gs = StringContainsQ[#, "GS"] & /@ team /. {True -> 1, False -> 0};
  dal = StringContainsQ[#, "DAL"] & /@ team /. {True -> 1, False -> 0};
  lac = StringContainsQ[#, "LAC"] & /@ team /. {True -> 1, False -> 0};
  okc = StringContainsQ[#, "OKC"] & /@ team /. {True -> 1, False -> 0};
  ny = StringContainsQ[#, "NY"] & /@ team /. {True -> 1, False -> 0};
  hou = StringContainsQ[#, "HOU"] & /@ team /. {True -> 1, False -> 0};
  mil = StringContainsQ[#, "MIL"] & /@ team /. {True -> 1, False -> 0};
  pho = StringContainsQ[#, "Pho"] & /@ team /. {True -> 1, False -> 0};
  por = StringContainsQ[#, "Por"] & /@ team /. {True -> 1, False -> 0};
  ind = StringContainsQ[#, "Ind"] & /@ team /. {True -> 1, False -> 0};
  
  m = Join[
    A, {sg, pg, -1*pg, g, pf, sf, f, s, p, 
     cen, -1*cen1, -1*bos, -1*min, -1*cle, -1*mem, -1*gs, -1*dal, -1*
      lac, -1*okc, -1*ny, -1*hou, -1*mil, -1*pho, -1*den, -1*por, -1*
      ind}];
  b = {-50000, -8, 8, 1, 1, -3, 3, 1, 1, 3, 2, 2, 
    1, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2};
  res = LinearProgramming[c, m, b, ConstantArray[{0, 1}, Length@c], 
    Integers];
  Pick[fantasyData[[All, {Name, algo, Pos, Team, Salary}]], # == 1 & /@
     res]]



RandomForestRoster = generateRosterCombined[RandomForest]

AdaBoostRoster = generateRosterCombined[AdaBoost]

NN = generateRosterCombined[NeuralNetwork]

rosterTypes = {"NeuralNetwork", "RandomForest", "Adaboost"}

rosters = {NN, RandomForestRoster, AdaBoostRoster};

pplayers = Map[(#[[1]] &), rosters, {2}];

rosterWithInfo = (Join[{rosterTypes[[#]]}, pplayers[[#]]] &) /@ 
   Range[Length@rosters];
rosterWithInfo = 
  Join[{{"Strategy", "p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8"}},
    rosterWithInfo];

Export["/Users/marek5050/machinelearning/NBA/data/generatedRosters2/" \
<> date <> ".csv", rosterWithInfo]


