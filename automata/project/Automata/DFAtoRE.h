#include <memory>
#include <utility>
#include <iostream>
#include <vector>
#include <unordered_map>
#include <algorithm>

#include "DFAutomaton.h"
#include "NFAutomaton.h"

#include "RegexState.h"
#include "IRegex.h"
#include "PhiRegex.h"
#include "LiteralRegex.h"
#include "EpsilonRegex.h"
#include "UnionRegex.h"
#include "ConcatRegex.h"
#include "ClosureRegex.h"
#include "HashExtensions.h"

typedef std::string State;
typedef std::string Char;

std::shared_ptr<IRegex> concatRE(std::shared_ptr<IRegex> left, std::shared_ptr<IRegex> right);
std::shared_ptr<IRegex> unifyRE(std::shared_ptr<IRegex> left, std::shared_ptr<IRegex> right);
std::shared_ptr<IRegex> closeRE(std::shared_ptr<IRegex> in);
std::shared_ptr<IRegex> DFAtoRE(DFAutomaton<std::string, std::string>& DFA);
std::shared_ptr<IRegex> NFAtoRE(NFAutomaton<std::string, std::string>& NFA);

class REAutomaton
{
private:
	std::vector<State> states;
	State startState;
	std::vector<State> acceptStates;

	std::unordered_map<State, std::unordered_map<State, std::shared_ptr<IRegex>>> transitionMap;

public:
	REAutomaton(DFAutomaton<std::string, std::string>& DFA){	// Create an REAutomaton that mirrors an existing DFA

		for (State from : DFA.GetStates().getItems()){
			for (State to : DFA.GetStates().getItems()){
				transitionMap[from][to] = std::make_shared<PhiRegex>();
			}
		}

		for (State state : DFA.GetStates().getItems()){
			states.push_back(state);
			for (Char trans : DFA.GetAlphabet().getItems()){
				if (DFA.PerformTransition(state, trans) != ""){
					this->addTransition(state, DFA.PerformTransition(state, trans), std::make_shared<LiteralRegex>(trans));
				}
			}
		}

		startState = DFA.getStartState();

		for (State state : DFA.getAcceptingStates().getItems()){
			acceptStates.push_back(state);
		}
	}

	REAutomaton(NFAutomaton<std::string, std::string>& NFA){	// Create an REAutomaton that mirrors an existing NFA

		for (State from : NFA.GetStates().getItems()){
			for (State to : NFA.GetStates().getItems()){
				transitionMap[from][to] = std::make_shared<PhiRegex>();
			}
		}

		for (State state : NFA.GetStates().getItems()){
			states.push_back(state);
			for (Char trans : NFA.GetAlphabet().getItems()){
				if (!(NFA.PerformTransition(state, trans).getIsEmpty())){
					for (auto toState : NFA.PerformTransition(state, trans).getItems())
						this->addTransition(state, toState, std::make_shared<LiteralRegex>(trans));
				}
			}
		}

		startState = NFA.getStartState();

		for (State state : NFA.getAcceptingStates().getItems()){
			acceptStates.push_back(state);
		}
	}

	REAutomaton(REAutomaton* originalREA, State acceptState){	// Create a duplicate REAutomaton that only has a single accept state
		this->states = originalREA->states;
		this->startState = originalREA->startState;
		this->transitionMap = originalREA->transitionMap;

		this->acceptStates.push_back(acceptState);
	}

	void addTransition(State from, State to, std::shared_ptr<IRegex> RE){
		this->transitionMap[from][to] = unifyRE(transitionMap[from][to], RE);
	}

	std::shared_ptr<IRegex> toRE(){

		std::shared_ptr<IRegex> finalRegex = std::make_shared<PhiRegex>();

		for (State acceptState : acceptStates){		// In a sub-REAutomaton with only one accept state
			REAutomaton REA(this, acceptState);

			// Reduce the REA to 2 states

			while (REA.states.size() > 2 || (REA.states.size() == 2 && REA.startState == REA.acceptStates[0])){

				// Find a removable state s 			(s = neither start nor accept)
				State s;
				for (State state : REA.states){
					if (state != REA.startState && state != REA.acceptStates[0]) s = state;
				}

				// Find S : delta(s, S) == s 			(s -> s)

				std::shared_ptr<IRegex> S = REA.transitionMap[s][s];

				for (State q : REA.states){
					if (q != s){

						// Find Q : delta(q, Q) = s			(q -> s)

						std::shared_ptr<IRegex> Q = REA.transitionMap[q][s];

						for (State p : REA.states){
							if (p != s){

								// Find P : delta(s, P) = p		(s -> p)

								std::shared_ptr<IRegex> P = REA.transitionMap[s][p];

								// Find R : delta(q, R) = p		(q -> p)

								std::shared_ptr<IRegex> R = REA.transitionMap[q][p];

								// New P = (R + QS*P)

								std::shared_ptr<IRegex> newP = unifyRE(R, concatRE(concatRE(Q, closeRE(S)), P));

								REA.transitionMap[q][p] = newP;
							}
						}
					}
				}

				// Remove every trace of State s

				REA.states.erase(std::find(REA.states.begin(), REA.states.end(), s));	// Remove s
				REA.transitionMap.erase(s);												// Remove every transition from s
				for (State state : REA.states){
					REA.transitionMap[state].erase(s);									// Remove every transition to s
				}
			}
			// Interpret the reduced REA:

			std::shared_ptr<IRegex> R = REA.transitionMap[REA.startState][REA.startState];				// start 	-> 	start	
			std::shared_ptr<IRegex> S = REA.transitionMap[REA.startState][REA.acceptStates[0]]; 		// start 	-> 	end		
			std::shared_ptr<IRegex> T = REA.transitionMap[REA.acceptStates[0]][REA.startState];			// end 		-> 	start	
			std::shared_ptr<IRegex> U = REA.transitionMap[REA.acceptStates[0]][REA.acceptStates[0]]; 	// end 		-> 	end		

			std::shared_ptr<IRegex> thisRegex = std::make_shared<PhiRegex>();

			if (REA.transitionMap.size() > 1){
				thisRegex = concatRE(closeRE(unifyRE(R, concatRE(concatRE(S, closeRE(U)), T))), concatRE(S, closeRE(U)));
			}
			else {
				thisRegex = closeRE(R);
			}
			finalRegex = unifyRE(finalRegex, thisRegex);
		}

		return finalRegex;
	}
};