import {
    Alert, AlertDescription,
    AlertIcon, AlertTitle,
    Box,
    Card,
    CardBody,
    Button,
    HStack,
    Icon,
    Skeleton,
    Stack,
    StackDivider,
    Text,
    VStack
} from "@chakra-ui/react";
import {ArbitrageGroup, ArbitrageOpportunity, HistoricArbitrage} from "../types/Arbitrage"
import React, {useState, useEffect} from "react";
import { motion } from "framer-motion";
import {ChevronLeftIcon, ArrowForwardIcon} from "@chakra-ui/icons";
import moment from "moment";
import {useCurrentArbitragesQuery, useHistoricArbitragesQuery} from "../store/services/arbitrage.ts";

const HistoricArbitrageItem: React.FC<{hist: HistoricArbitrage}> = ({hist}) => {

    return (

        <Card variant="filled" bgColor="purple.300" textColor={"white"}>
            <CardBody>
                <HStack align="center" justify="space-between">
                    <Text>Pair: {hist.tradingPair}</Text>
                    <Text>
                        {hist.buyExchange} <Icon as={ArrowForwardIcon}/> {hist.sellExchange}
                    </Text>
                    <Text>
                        {moment.utc(hist.start).local().format("DD.MM.YY HH:mm")} - {moment.utc(hist.end).local().format("DD.MM.YY HH:mm")}
                    </Text>
                    <Text>
                        Dauer: {(() => {
                            const dur = moment.duration(hist.runTime,'seconds');
                            return `${dur.minutes()} minutes and ${dur.seconds()} seconds`;
                        })()}
                    </Text>
                </HStack>
            </CardBody>
        </Card>
    )
}

function ArbitrageHistoryList() {

    const {data, isLoading, isError, isSuccess, error} = useHistoricArbitragesQuery({})

    return (
        <VStack
            divider={<StackDivider borderColor='gray.200'/>}
            spacing={4}
            align='stretch'
        >
            {
                (isLoading && !data ) && <Stack>
                    <Skeleton height='20px' />
                    <Skeleton height='20px' />
                    <Skeleton height='20px' />
                </Stack>
            }
            {
                (isSuccess && data.length== 0) &&
                <Alert status='info'>
                    <AlertIcon />
                    <AlertTitle>No Historic Arbitrages found :(</AlertTitle>
                    <AlertDescription></AlertDescription>
                </Alert>
            }
            {
                isError &&
                <Alert status='error'>
                    <AlertIcon />
                    <AlertTitle>Error fetching data</AlertTitle>
                    <AlertDescription>{error.message}</AlertDescription>
                </Alert>
            }
            {
              isSuccess &&  data.map((h,index) => (
                  h.runTime > 60 && <HistoricArbitrageItem hist={h} key={index} />))
            }
        </VStack>
    )
}

export default ArbitrageHistoryList;
