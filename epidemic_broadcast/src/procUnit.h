//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Lesser General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
// 
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Lesser General Public License for more details.
// 
// You should have received a copy of the GNU Lesser General Public License
// along with this program.  If not, see http://www.gnu.org/licenses/.
// 

#ifndef __EPIDEMIC_BROADCAST_PROCUNIT_H_
#define __EPIDEMIC_BROADCAST_PROCUNIT_H_

#include <omnetpp.h>
#include "inet/common/packet/Packet.h"
#include "host.h"

using namespace omnetpp;
using namespace inet;
/**
 * TODO - Generated class
 */
class ProcUnit : public cSimpleModule
{
    private:
        cMessage* slotBeep_;
        cMessage* opStop_;
        cMessage* broadcast_;
        Status procUnitStatus_;

        double slotLength_;
        double timeToNextSlot_;
        long attempts_;

        double p_;

        //signal variables
        //TODO: fix code to collect statistics

        // number of coin tosses
        simsignal_t attemptsSignal_;
        simsignal_t reachSignal_;
    protected:
        virtual void initialize();
        virtual double getTimeToNextSlot();
        virtual void handleMessage(cMessage *msg);
        virtual void handleBroadcastMessage(cMessage *msg);
        virtual void handleSlotBeepMessage(cMessage *msg);
        virtual void handleStopOperationMessage();
        // prepare and send a Inet.Packet to the out gate
        virtual void sendPkt(Packet *packet);

    public:
        ProcUnit();
        ~ProcUnit();

};

#endif
