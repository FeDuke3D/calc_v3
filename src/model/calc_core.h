#ifndef SRC_CALC_CORE_H_
#define SRC_CALC_CORE_H_

#include <stack>
#include <list>
#include <string>
#include <regex>
#include <iostream>
#include <sstream>
#include <cmath>
//#include <pcre.h>

namespace s21 {

enum Funct {kNumber, kMinus, kPlus, kMult, kDiv, kMod, kPow, kUMinus, kUPlus,
        kCos, kSin, kTan, kAcos, kAsin, kAtan, kSqrt, kLn, kLog, kLeftPar,
        kRightPar, kVarX};
typedef std::pair<Funct, double> Token;
class SyntaxError : public std::exception {};
class AlgorithmError : public std::exception {};

class Model {
 private:
  std::list<Token> expression_{};

  // big methods
  std::list<Token> Parse(std::string source);
  std::list<Token> ShuntingYard(std::list<Token> source);

  // small methods
  void RemoveSpaces(std::string *src);
  void FixImplicitPar(std::list<Token> *src);
  void FixUnary(std::list<Token> *src);
  void MarkUnary(Token *src);
  void FixImplicitMult(std::list<Token> *src);
  bool IsMathFunction(Funct src);
  bool IsBinaryOperation(Funct src);
  bool IsUnary(Funct src);
  bool IsAnyFunction(Funct src);
  bool IsNumber(Funct src);
  int Priority(Funct src);

  // debug
  std::string TokenToStr(Token src);

 public:
  void ChangeExpr(const std::string &source);
  double CalcProc(double param);
  bool HasVarX();

  // debug
  std::string ExprToStr();
};

}  // namespace s21

#endif  // SRC_CALC_CORE_H_
