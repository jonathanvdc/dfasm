#include "DFAtoRE.h"

std::shared_ptr<IRegex> concatRE(std::shared_ptr<IRegex> left, std::shared_ptr<IRegex> right){
	if (left->ToString() == "\\e"){
		return right;
	}
	else if (right->ToString() == "\\e"){
		return left;
	}
	else if (left->ToString() == "\\p" || right->ToString() == "\\p"){
		return std::make_shared<PhiRegex>();
	}

	return std::make_shared<ConcatRegex>(left, right);
}

std::shared_ptr<IRegex> unifyRE(std::shared_ptr<IRegex> left, std::shared_ptr<IRegex> right){
	if (left->ToString() == "\\p"){
		return right;
	}
	else if (right->ToString() == "\\p"){
		return left;
	}
	else if (right->ToString() == left->ToString()){
		return left;
	}

	return std::make_shared<UnionRegex>(left, right);
}

std::shared_ptr<IRegex> closeRE(std::shared_ptr<IRegex> in){
	if (in->ToString() == "\\e" || in->ToString() == "\\p"){
		return std::make_shared<EpsilonRegex>();
	}
	return std::make_shared<ClosureRegex>(in);
}

std::shared_ptr<IRegex> DFAtoRE(DFAutomaton<std::string, std::string>& DFA){

	REAutomaton REA(DFA);

	auto pointer = REA.toRE();

	return pointer;

}

std::shared_ptr<IRegex> NFAtoRE(NFAutomaton<std::string, std::string>& NFA){

	REAutomaton REA(NFA);

	auto pointer = REA.toRE();

	return pointer;

}