import { createContext, useContext, useEffect, useState } from 'react'

interface FlowState {
  step: number
  email?: string
  plaidLinkToken?: string
  personaStatus?: string
  docusign?: boolean
}

const FlowCtx = createContext<[FlowState, (s: FlowState) => void]>([{ step: 0 }, () => {}])

export function useFlow() {
  return useContext(FlowCtx)
}

export default function FlowProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<FlowState>(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('kyc-flow')
      return saved ? JSON.parse(saved) : { step: 0 }
    }
    return { step: 0 }
  })

  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('kyc-flow', JSON.stringify(state))
    }
  }, [state])

  return <FlowCtx.Provider value={[state, setState]}>{children}</FlowCtx.Provider>
}

export function FlowSteps() {
  const [state, setState] = useFlow()
  switch (state.step) {
    case 0:
      return (
        <form
          onSubmit={(e) => {
            e.preventDefault()
            setState({ ...state, step: 1, email: (e.target as any).email.value })
          }}
        >
          <input name="email" placeholder="Email" />
          <button type="submit">Next</button>
        </form>
      )
    case 1:
      return (
        <button
          onClick={() => {
            setState({ ...state, step: 2, plaidLinkToken: 'dummy' })
          }}
        >
          Link Bank (Plaid)
        </button>
      )
    case 2:
      return (
        <button
          onClick={() => {
            setState({ ...state, step: 3, personaStatus: 'passed' })
          }}
        >
          Run Persona
        </button>
      )
    case 3:
      return (
        <button
          onClick={() => {
            setState({ ...state, step: 4, docusign: true })
          }}
        >
          DocuSign
        </button>
      )
    default:
      return <div>Complete</div>
  }
}
