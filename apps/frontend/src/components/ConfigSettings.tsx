import React, { useEffect, useState } from 'react';
import {
    useToast,
    Button,
    ButtonGroup,
    SimpleGrid,
    Input,
    HStack,
    InputGroup,
    InputRightAddon,
    Card,
    CardHeader,
    CardBody,
    Text,
    FormControl,
    FormErrorMessage
} from '@chakra-ui/react';
import { useGetConfigsQuery, useAddConfigsMutation } from '../redux/services/config';
import { Formik, Field, Form } from 'formik';
import * as Yup from 'yup';
import {ConfigResponse, UserConfig} from "../types/UserConfig.ts";  // Import Yup

// Define the validation schema using Yup
const validationSchema = Yup.object({
    configs: Yup.array().of(
        Yup.object({
            maxAmount: Yup.number()
                .min(0, 'Max amount must be greater than or equal to 0') // Validation for values >= 0
                .required('Max amount is required')
                .typeError('Max amount must be a valid number')  // Ensures the field is a number
        })
    )
});

interface ConfigItemProps {
    config: UserConfig;
    index: number;
}

const ConfigItem: React.FC<ConfigItemProps> = ({ config, index }) => {
    return (
        <Card>
            <CardHeader>{config.exchangeLong}</CardHeader>
            <CardBody>
                <HStack>
                    <Text>Maximalbetrag: </Text>
                    <InputGroup size='sm'>
                        <Field name={`configs[${index}].maxAmount`}>
                            {({ field, form }: any) => (
                                <FormControl isInvalid={form.errors.configs && form.errors.configs[index] && form.touched.configs && form.touched.configs[index]}>
                                    <Input
                                        {...field}
                                        type="number"
                                        placeholder="max amount"
                                        onChange={(e) => form.setFieldValue(`configs[${index}].maxAmount`, e.target.value)}
                                    />
                                    <FormErrorMessage>
                                            {form.errors.configs && form.errors.configs[index] && form.errors.configs[index].maxAmount}
                                    </FormErrorMessage>
                                </FormControl>
                            )}
                        </Field>
                        <InputRightAddon>USDT</InputRightAddon>
                    </InputGroup>
                </HStack>
            </CardBody>
        </Card>
    );
};

const ConfigList: React.FC = () => {
    const { data, isSuccess: loadSuccess } = useGetConfigsQuery({});
    const [addConfigs, { isSuccess: saveSuccess , isLoading}] = useAddConfigsMutation();
    const [editableData, setEditableData] = useState<UserConfig[]>([]);
    const toast = useToast();

    useEffect(() => {
        if (data) {
            setEditableData([...data]); // Set the editableData when data is fetched
        }
    }, [data]);

    const handleSubmit = async (values: any) => {
        const request_configs: ConfigResponse[] = values.configs.map((item: UserConfig) => {
            return {
                max_amount: item.maxAmount,
                exchange_key: item.exchangeShort,
            };
        });

        try {
            await addConfigs(request_configs).unwrap();
            toast({
                status: 'success',
                title: 'Success',
                description: 'Config successfully saved',
                isClosable: true,
            });
        } catch {
            toast({
                status: 'error',
                title: 'Error',
                description: 'Error while saving configs',
                isClosable: true,
            });
        }
    };

    return (
        <Formik
            initialValues={{
                configs: editableData || [], // Provide an empty array as a fallback
            }}
            validationSchema={validationSchema} // Pass the validation schema to Formik
            onSubmit={handleSubmit}
            enableReinitialize={true} // Allows the form to update when editableData changes
        >
            {({ values }) => (
                <>
                    {/* Conditionally render form or loading spinner */}
                    {loadSuccess && editableData.length > 0 ? (
                        <Form>
                            <SimpleGrid spacing={2}>
                                {values.configs.map((config: UserConfig, index: number) => (
                                    <ConfigItem key={index} config={config} index={index} />
                                ))}
                            </SimpleGrid>
                            <ButtonGroup variant="outline" spacing={6}>
                                <Button>Cancel</Button>
                                <Button type="submit" colorScheme="purple" isLoading={isLoading}>
                                    Save
                                </Button>
                            </ButtonGroup>
                        </Form>
                    ) : (
                        // Show a loading message or spinner while data is being fetched
                        <Text>Loading configurations...</Text>
                    )}
                </>
            )}
        </Formik>
    );
};

export default ConfigList
