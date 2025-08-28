import React from 'react';
import {Field, Formik} from "formik";
import {
    Box,
    Button,
    Flex,
    FormControl, FormErrorMessage,
    FormLabel,
    Input, useToast,
    VStack
} from "@chakra-ui/react";
import { useDispatch } from "react-redux";
import { useEffect } from "react";
import { useNavigate } from "react-router"
import {useLoginMutation} from "../redux/services/auth"
import {setCredentials} from "../redux/slices/authSlice";


const LoginForm: React.FC = () => {
    const dispatch = useDispatch();
    const navigate = useNavigate();
    const toast = useToast()

    //const { register, errors, handleSubmit } = useForm();
    const [login, {isLoading, isError, error}] = useLoginMutation();

    useEffect(() => {
        if (isError) {
            console.log(error);
        }
    }, [isError]);

    return (
        <Flex bg="gray.100" align="center" justify="center" h="100vh">
            <Box bg="white" p={6} rounded="md" w={64}>
                <Formik
                    initialValues={{
                        username: "",
                        password: ""
                    }}
                    onSubmit={async (data) => {
                        try {
                            const token = await login(data).unwrap()
                            dispatch(setCredentials({token: token.access_token}))
                            navigate('/dashboard')
                        } catch (err) {
                            toast({
                                status: 'error',
                                title: 'Error',
                                description: err.error,
                                isClosable: true,
                            })

                        }
                    }
                    }
                >
                    {({ handleSubmit, errors, touched }) => (
                        <form onSubmit={handleSubmit}>
                            <VStack spacing={4} align="flex-start">
                                <FormControl>
                                    <FormLabel htmlFor="username">Username</FormLabel>
                                    <Field
                                        as={Input}
                                        id="username"
                                        name="username"
                                        type="input"
                                        variant="filled"
                                    />
                                </FormControl>
                                <FormControl isInvalid={!!errors.password && touched.password}>
                                    <FormLabel htmlFor="password">Password</FormLabel>
                                    <Field
                                        as={Input}
                                        id="password"
                                        name="password"
                                        type="password"
                                        variant="filled"
                                        validate={(value: string) => {
                                            let error;

                                            if (value.length < 4) {
                                                error = "Password must contain at least 6 characters";
                                            }

                                            return error;
                                        }}
                                    />
                                    <FormErrorMessage>{errors.password}</FormErrorMessage>
                                </FormControl>
                                <Button type="submit" colorScheme="purple" width="full" isLoading={isLoading}>
                                    Login
                                </Button>
                            </VStack>
                        </form>
                    )}
                </Formik>
            </Box>
        </Flex>
    );
};

export default LoginForm;
