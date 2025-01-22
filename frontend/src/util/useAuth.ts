import { useMemo } from 'react'
import { useSelector } from 'react-redux'
import { selectCurrentUser } from '../store/slices/authSlice'

export const useAuth = () => {
    const token = useSelector(selectCurrentUser)

    return useMemo(() => ({ token }), [token])
}