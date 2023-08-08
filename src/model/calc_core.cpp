#include "calc_core.h"

namespace s21 {

// splits input string into Tokens
std::list<Token> Model::Parse(std::string source) {
  setlocale(LC_ALL, "en_US.UTF-8");
  std::list<Token> res{};
  std::regex pattern("[0-9]+(\\.[0-9]+)?([eE][\\+-]?[0-9]+)?|[-\\(\\)\\+\\*/"
          "\\^]|mod|cos|sin|tan|acos|asin|atan|sqrt|ln|log|x");
  Token elem{};
  std::smatch pmatch;
  RemoveSpaces(&source);
  while (std::regex_search(source, pmatch, pattern,
          std::regex_constants::match_continuous)) {
    if (pmatch.str()[0] >= '0' && pmatch.str()[0] <= '9') {
      elem.first = Funct::kNumber;
      try {
        elem.second = std::stod(pmatch.str());
      } catch (...) {
        throw SyntaxError();
      }
    } else {
      if (pmatch.str() == "-") elem.first = Funct::kMinus;
      else if (pmatch.str() == "+") elem.first = Funct::kPlus;
      else if (pmatch.str() == "*") elem.first = Funct::kMult;
      else if (pmatch.str() == "/") elem.first = Funct::kDiv;
      else if (pmatch.str() == "^") elem.first = Funct::kPow;
      else if (pmatch.str() == "(") elem.first = Funct::kLeftPar;
      else if (pmatch.str() == ")") elem.first = Funct::kRightPar;
      else if (pmatch.str() == "mod") elem.first = Funct::kMod;
      else if (pmatch.str() == "cos") elem.first = Funct::kCos;
      else if (pmatch.str() == "sin") elem.first = Funct::kSin;
      else if (pmatch.str() == "tan") elem.first = Funct::kTan;
      else if (pmatch.str() == "acos") elem.first = Funct::kAcos;
      else if (pmatch.str() == "asin") elem.first = Funct::kAsin;
      else if (pmatch.str() == "atan") elem.first = Funct::kAtan;
      else if (pmatch.str() == "sqrt") elem.first = Funct::kSqrt;
      else if (pmatch.str() == "ln") elem.first = Funct::kLn;
      else if (pmatch.str() == "log") elem.first = Funct::kLog;
      else if (pmatch.str() == "x") elem.first = Funct::kVarX;
    }
    res.push_back(elem);
    source = pmatch.suffix().str();
  }
  if (!source.empty()) throw SyntaxError();
  FixImplicitPar(&res);
  FixUnary(&res);
  FixImplicitMult(&res);
  return res;
}

// sorts list according to shunting yard algorithm,
// turning it into reverse polish notation
std::list<Token> Model::ShuntingYard(std::list<Token> source) {
  std::list<Token> res{};
  std::stack<Token> tmp{};
  while (!source.empty()) {
    if (IsNumber(source.front().first)) {
      res.push_back(source.front());
      source.pop_front();
    } else if (source.front().first == Funct::kLeftPar) {
      tmp.push(source.front());
      source.pop_front();
    } else if (IsAnyFunction(source.front().first)) {
      int associativity{};
      if (source.front().first == Funct::kPow) associativity++;
      while (!tmp.empty() && Priority(tmp.top().first) <=
              Priority(source.front().first) - associativity) {
        res.push_back(tmp.top());
        tmp.pop();
      }
      tmp.push(source.front());
      source.pop_front();
    } else if (source.front().first == Funct::kRightPar) {
      while (!tmp.empty() && tmp.top().first != Funct::kLeftPar) {
        res.push_back(tmp.top());
        tmp.pop();
      }
      if (tmp.empty()) throw SyntaxError();
      tmp.pop();
      source.pop_front();
    }
  }
  while (!tmp.empty()) {
    if (tmp.top().first == Funct::kLeftPar) throw SyntaxError();
    res.push_back(tmp.top());
    tmp.pop();
  }
  return res;
}

// removes spaces from string
void Model::RemoveSpaces(std::string *src) {
  auto i = src->begin();
  while (i != src->end()) {
    if (*i == ' ')
      i = src->erase(i);
    else
      ++i;
  }
}

// finds and adds missing parentheses
void Model::FixImplicitPar(std::list<Token> *src) {
  auto iter = src->begin();
  while (iter != src->end()) {
    if (IsMathFunction(iter->first)) {
      ++iter;
      if (iter->first != Funct::kLeftPar) {
        iter = src->insert(iter, {Funct::kLeftPar, 0});
        auto j = iter;
        while (!IsNumber(j->first) && j != src->end())
          ++j;
        if (j == src->end()) throw SyntaxError();
        while (IsNumber(j->first))
          ++j;
        src->insert(j, {Funct::kRightPar, 0});
      }
    } else {
      ++iter;
    }
  }
}

// finds where plus or minus Tokens means unary and replaces
void Model::FixUnary(std::list<Token> *src) {
  bool flag{true};
  for (auto i = src->begin(); i != src->end(); ++i) {
    if (flag) MarkUnary(&(*i));
    if (IsBinaryOperation(i->first) || IsUnary(i->first) ||
            i->first == Funct::kLeftPar)
      flag = true;
    else
      flag = false;
  }
}

// turns plus/minus Tokens to unary
void Model::MarkUnary(Token *src) {
  if (src->first == Funct::kMinus)
    src->first = Funct::kUMinus;
  else if (src->first == Funct::kPlus)
    src->first = Funct::kUPlus;
}

// inserts multiplication Tokens where they are omited
void Model::FixImplicitMult(std::list<Token> *src) {
  bool flag{false};
  for (auto i = src->begin(); i != src->end(); ++i) {
    if (flag) {
      if (i->first == Funct::kLeftPar || IsNumber(i->first) ||
                IsMathFunction(i->first))
        i = src->insert(i, {Funct::kMult, 0});
    }
    if (i->first == Funct::kRightPar || IsNumber(i->first))
      flag = true;
    else
      flag = false;
  }
}

bool Model::IsMathFunction(Funct src) {
  return (src < Funct::kCos || src > Funct::kLog) ? false : true;
}

bool Model::IsBinaryOperation(Funct src) {
  return (src < Funct::kMinus || src > Funct::kPow) ? false : true;
}

bool Model::IsUnary(Funct src) {
  return (src == Funct::kUMinus || src == Funct::kUPlus);
}

bool Model::IsAnyFunction(Funct src) {
  return (IsMathFunction(src) || IsBinaryOperation(src) || IsUnary(src));
}

bool Model::IsNumber(Funct src) {
  return (src == Funct::kNumber || src == Funct::kVarX);
}

//  priority:
//  1 Functions
//  2 um up
//  3 ^
//  4 *  /  mod
//  5 +  -
int Model::Priority(Funct src) {
  int res(6);
  if (IsMathFunction(src)) res = 1;
  else if (IsUnary(src)) res = 2;
  else if (src == Funct::kPow) res = 3;
  else if (src > Funct::kPlus && src < Funct::kPow) res = 4;
  else if (src == Funct::kMinus || src == Funct::kPlus) res = 5;
  return res;
}

// changes Model.expression_ by parsing and sorting input string
void Model::ChangeExpr(const std::string &source) {
  expression_ = Parse(source);
  expression_ = ShuntingYard(expression_);
}

// performs calculations using param as kVarX substitute
double Model::CalcProc(double param) {
  if (expression_.empty()) throw SyntaxError();
  std::stack<double> tmp{};
  for (auto i : expression_) {
    if (i.first == Funct::kVarX) {
      tmp.push(param);
    } else if (i.first == Funct::kNumber) {
      tmp.push(i.second);
    } else if (!tmp.empty()) {
      if (i.first == Funct::kUMinus) {
        tmp.top() *= -1;
      } else if (i.first == Funct::kCos) {
        tmp.top() = cos(tmp.top());
      } else if (i.first == Funct::kSin) {
        tmp.top() = sin(tmp.top());
      } else if (i.first == Funct::kTan) {
        tmp.top() = tan(tmp.top());
      } else if (i.first == Funct::kAcos) {
        tmp.top() = acos(tmp.top());
      } else if (i.first == Funct::kAsin) {
        tmp.top() = asin(tmp.top());
      } else if (i.first == Funct::kAtan) {
        tmp.top() = atan(tmp.top());
      } else if (i.first == Funct::kSqrt) {
        tmp.top() = sqrt(tmp.top());
      } else if (i.first == Funct::kLn) {
        tmp.top() = log(tmp.top());
      } else if (i.first == Funct::kLog) {
        tmp.top() = log10(tmp.top());
      } else if (i.first == Funct::kUPlus) {
        tmp.top() *= 1;
      } else if (tmp.size() > 1) {
        double val = tmp.top();
        tmp.pop();
        if (i.first == Funct::kMinus) tmp.top() -= val;
        else if (i.first == Funct::kPlus) tmp.top() += val;
        else if (i.first == Funct::kMult) tmp.top() *= val;
        else if (i.first == Funct::kDiv) tmp.top() /= val;
        else if (i.first == Funct::kMod) tmp.top() = fmod(tmp.top(), val);
        else if (i.first == Funct::kPow) tmp.top() = pow(tmp.top(), val);
      } else {
        throw SyntaxError();
      }
    } else {
      throw SyntaxError();
    }
  }
  if (tmp.size() > 1) throw AlgorithmError();
  return tmp.top();
}

// creates a string out of Model.expression for test and debug purposes
std::string Model::ExprToStr() {
  std::string res{};
  for (auto i : expression_) {
    res += TokenToStr(i);
    res += " ";
  }
  return res;
}

// creates string out of single Token
std::string Model::TokenToStr(Token src) {
  std::string res{};
  if (src.first == Funct::kNumber) {
    std::ostringstream strs;
    strs << src.second;
    res = strs.str();
  } else if (src.first == Funct::kMinus) {
    res = "-";
  } else if (src.first == Funct::kPlus) {
    res = "+";
  } else if (src.first == Funct::kMult) {
    res = "*";
  } else if (src.first == Funct::kDiv) {
    res = "/";
  } else if (src.first == Funct::kPow) {
    res = "^";
  } else if (src.first == Funct::kMod) {
    res = "mod";
  } else if (src.first == Funct::kUMinus) {
    res = "u-";
  } else if (src.first == Funct::kUPlus) {
    res = "u+";
  } else if (src.first == Funct::kCos) {
    res = "cos";
  } else if (src.first == Funct::kSin) {
    res = "sin";
  } else if (src.first == Funct::kTan) {
    res = "tan";
  } else if (src.first == Funct::kAcos) {
    res = "acos";
  } else if (src.first == Funct::kAsin) {
    res = "asin";
  } else if (src.first == Funct::kAtan) {
    res = "atan";
  } else if (src.first == Funct::kSqrt) {
    res = "sqrt";
  } else if (src.first == Funct::kLn) {
    res = "ln";
  } else if (src.first == Funct::kLog) {
    res = "log";
  } else if (src.first == Funct::kLeftPar) {
    res = "(";
  } else if (src.first == Funct::kRightPar) {
    res = ")";
  } else if (src.first == Funct::kVarX) {
    res = "x";
  }
  return res;
}

bool Model::HasVarX() {
    bool res {false};
    for (auto i : expression_)
        if (i.first == Funct::kVarX) res = true;
    return res;
}

}  // namespace s21
